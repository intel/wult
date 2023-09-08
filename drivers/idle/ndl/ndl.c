// SPDX-License-Identifier: GPL-2.0-only
/*
 * Copyright (C) 2019-2021 Intel Corporation
 * Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>
 */

#define pr_fmt(fmt)	KBUILD_MODNAME ": " fmt

#include <linux/bitfield.h>
#include <linux/debugfs.h>
#include <linux/err.h>
#include <linux/fs.h>
#include <linux/module.h>
#include <linux/netdevice.h>
#include <linux/pci.h>
#include <linux/string.h>
#include <linux/types.h>

#define DRIVER_NAME "ndl"
#define NDL_VERSION "1.0"

#define I210_RR2DCDELAY 0x5BF4
#define I210_RR2DCDELAY_INCR 16
#define I210_TXDCTL	0xE028
#define I210_WTHRESH_MASK	GENMASK(20, 16)

/* Name of the network device to attach to. */
static char *ifname;

/* The network device corresponding to the 'ifname' interface. */
static struct net_device *i210_ndev;

/* The PCI device corresponding to the 'ifname' interface. */
static struct pci_dev *i210_pdev;

/* The network device IO memory base address. */
static u8 __iomem *i210_iomem;

/* Driver's root debugfs directory. */
static struct dentry *dfsroot;

/* Saved DMA coalescing config. */
static int wthresh_save[4];

static ssize_t dfs_read_file(struct file *file, char __user *user_buf,
			     size_t count, loff_t *ppos)
{
	ssize_t res;
	u64 rtd;
	char buf[64];
	struct dentry *dent = file->f_path.dentry;

	res = debugfs_file_get(dent);
	if (res)
		return res;

	rtd = readl(&i210_iomem[I210_RR2DCDELAY]);
	rtd *= I210_RR2DCDELAY_INCR;
	snprintf(buf, sizeof(buf), "%llu", rtd);
	debugfs_file_put(dent);

	return simple_read_from_buffer(user_buf, count, ppos, buf, strlen(buf));
}

static const struct file_operations dfs_ops = {
	.read = dfs_read_file,
	.open = simple_open,
	.llseek = default_llseek,
};

static int dfs_create(void)
{
	struct dentry *dent;

	dfsroot = debugfs_create_dir(DRIVER_NAME, NULL);
	if (IS_ERR(dfsroot))
		return PTR_ERR(dfsroot);

	dent = debugfs_create_file("rtd", 0444, dfsroot, NULL, &dfs_ops);
	if (IS_ERR(dent)) {
		debugfs_remove(dfsroot);
		return PTR_ERR(dfsroot);
	}

	return 0;
}

/*
 * Disable DMA coalescing for the I210 device. This is done to avoid potential
 * latency spikes during the measurement.
 */
static void dma_coalescing_disable(void)
{
	int i;
	u32 val;

	for (i = 0; i <= 3; i++) {
		val = readl(&i210_iomem[I210_TXDCTL + i * 0x40]);
		wthresh_save[i] = FIELD_GET(I210_WTHRESH_MASK, val);
		val &= ~I210_WTHRESH_MASK;
		writel(val, &i210_iomem[I210_TXDCTL + i * 0x40]);
	}
}

/* Restore previosly saved DMA coalescing value */
static void dma_coalescing_restore(void)
{
	int i;
	u32 val;

	for (i = 0; i <= 3; i++) {
		val = readl(&i210_iomem[I210_TXDCTL + i * 0x40]);
		val |= FIELD_PREP(I210_WTHRESH_MASK, wthresh_save[i]);
		writel(val, &i210_iomem[I210_TXDCTL + i * 0x40]);
	}
}

/* Find the PCI device for a network device. */
static struct pci_dev * __init find_pci_device(const struct net_device *ndev)
{
	struct pci_dev *pdev = NULL;

	while ((pdev = pci_get_device(PCI_VENDOR_ID_INTEL, PCI_ANY_ID, pdev))
	       != NULL) {
		if (!pdev->driver || strcmp(pdev->driver->name, "igb"))
			/* I210 devices are managed by the 'igb' driver. */
			continue;
		if (pci_get_drvdata(pdev) == ndev)
			break;
	}

	return pdev;
}

static int ndl_do_init(void)
{
	int err;

	if (i210_ndev)
		return NOTIFY_DONE;

	i210_ndev = dev_get_by_name(&init_net, ifname);
	if (!i210_ndev) {
		pr_err("network device '%s' was not found\n", ifname);
		return -EINVAL;
	}

	i210_pdev = find_pci_device(i210_ndev);
	if (!i210_pdev) {
		pr_err("cannot find PCI device for network device '%s'\n",
		       i210_ndev->name);
		err = -EINVAL;
		goto error_put_ndev;
	}

	/* Get the base IO memory address. */
	i210_iomem = pci_ioremap_bar(i210_pdev, 0);

	err = dfs_create();
	if (err)
		goto error_put_pdev;

	dma_coalescing_disable();

	return 0;

error_put_pdev:
	pci_dev_put(i210_pdev);
	pci_iounmap(i210_pdev, i210_iomem);
error_put_ndev:
	dev_put(i210_ndev);
	i210_ndev = NULL;

	return err;
}

static void ndl_do_exit(void)
{
	dma_coalescing_restore();
	dev_put(i210_ndev);
	i210_ndev = NULL;
	pci_dev_put(i210_pdev);
	pci_iounmap(i210_pdev, i210_iomem);
	debugfs_remove_recursive(dfsroot);
}

static int ndl_netdevice_event(struct notifier_block *notifier,
			       unsigned long event, void *ptr)
{
	struct net_device *dev = netdev_notifier_info_to_dev(ptr);
	int err;

	if (dev != i210_ndev)
		return NOTIFY_DONE;

	switch (event) {
	case NETDEV_REGISTER:
		err = ndl_do_init();
		if (err)
			pr_err("init failed:%d\n", err);
		break;
	case NETDEV_UNREGISTER:
		ndl_do_exit();
		break;
	default:
		break;
	};

	return NOTIFY_DONE;
}

static struct notifier_block ndl_netdevice_notifier = {
	.notifier_call = ndl_netdevice_event,
};

/* Module initialization function. */
static int __init ndl_init(void)
{
	int err;

	if (!ifname) {
		pr_err("network interface name not specified\n");
		return -EINVAL;
	}

	err = ndl_do_init();
	if (err)
		return err;

	err = register_netdevice_notifier(&ndl_netdevice_notifier);
	if (err) {
		pr_err("failed to register notifier\n");
		ndl_do_exit();
	}

	return err;
}
module_init(ndl_init);

/* Module exit function. */
static void __exit ndl_exit(void)
{
	unregister_netdevice_notifier(&ndl_netdevice_notifier);

	if (!i210_ndev)
		return;

	ndl_do_exit();
}
module_exit(ndl_exit);

module_param(ifname, charp, 0644);
MODULE_PARM_DESC(ifname, "name of the network interface to use.");

MODULE_VERSION(NDL_VERSION);
MODULE_DESCRIPTION("the ndl driver.");
MODULE_AUTHOR("Artem Bityutskiy");
MODULE_LICENSE("GPL v2");
