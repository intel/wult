// SPDX-License-Identifier: GPL-2.0-only
/*
 * Copyright (C) 2019-2020, Intel Corporation
 * Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>
 */

#define DRIVER_NAME "wult_igb"

#include <linux/cpumask.h>
#include <linux/delay.h>
#include <linux/errno.h>
#include <linux/interrupt.h>
#include <linux/irqreturn.h>
#include <linux/ktime.h>
#include <linux/module.h>
#include <linux/pci.h>
#include <linux/preempt.h>
#include <linux/slab.h>
#include <asm/msr.h>
#include "wult.h"
#include "wult_igb.h"

static struct wult_trace_data_info tdata[] = {
	{ .name = "WarmupDelayCyc" },
	{ .name = "LatchDelayCyc" },
	{ NULL },
};

/* Read a 32-bit NIC register. */
static inline u32 read32(const struct network_adapter *nic, u32 reg)
{
	return readl(&nic->iomem[reg]);
}

/* Write a 32-bit NIC register. */
static inline void write32(const struct network_adapter *nic, u32 val, u32 reg)
{
	return writel(val, &nic->iomem[reg]);
}

/* Flush posted PCI writes. */
static inline void pci_flush_posted(const struct network_adapter *nic)
{
	read32(nic, I210_STATUS);
}

/*
 * Acknowledge NIC interrupt and do a sanity check.
 */
static int irq_ack_and_check(const struct network_adapter *nic)
{
	u32 icr, tsicr;

	icr = read32(nic, I210_ICR);
	tsicr = read32(nic, I210_TSICR);

	if (!(icr & I210_Ixx_TIME_SYNC) || !(tsicr & I210_TSIxx_TT0)) {
		WARN_ONCE(1, "spurious interrupt, ICR %#x, EICR %#x, TSICR %#x",
			  icr, read32(nic, I210_EICR), tsicr);
		return -EINVAL;
	}

	return 0;
}

static irqreturn_t interrupt_handler(int irq, void *data)
{
	int err;
	struct network_adapter *nic = data;

	wult_interrupt_start();

	err = irq_ack_and_check(nic);
	wult_interrupt_finish(err);

	return IRQ_HANDLED;
}

static bool irq_is_pending(struct network_adapter *nic)
{
	/* Reading ICS is the same as reading ICR, except it does not clear. */
	return read32(nic, I210_ICS) & I210_Ixx_TIME_SYNC;
}

static u64 get_time_before_idle(struct wult_device_info *wdi, u64 *adj_cyc)
{
	struct network_adapter *nic = wdi_to_nic(wdi);
	u64 ns, cyc1, cyc2, cyc3;

	/* A "warm up" read. */
	pci_flush_posted(nic);

	/* Latch the time. */
	cyc1 = rdtsc_ordered();
	read32(nic, I210_SYSTIMR);
	cyc2 = rdtsc_ordered();

	ns = read32(nic, I210_SYSTIML);
	ns += read32(nic, I210_SYSTIMH) * NSEC_PER_SEC;
	cyc3 = rdtsc_ordered();

	/*
	 * Ideally, time before idle is the moment this function exits. But we
	 * latch the time at the beginning of the function, then spend time
	 * reading from the NIC. Everything we do after NIC has latched the
	 * time is the overhead, and we try to calculate the adjustment for
	 * this overhead.
	 *
	 * For the first latch read operation, we assume that the overhead is
	 * half of the read delay. And then we need to adjust for the time read
	 * operations.
	 *
	 * Note, 'ns' is time in nanoseconds as seen by the NIC. 'adj_cyc' is
	 * count of cycles, measured by CPU. So not only these are different
	 * units, but also different observers.
	 */
	*adj_cyc = (cyc2 - cyc1)/2 + (cyc3 - cyc2);

	return ns;
}

static u64 get_time_after_idle(struct wult_device_info *wdi, u64 cyc1,
		               u64 *adj_cyc)
{
	struct network_adapter *nic = wdi_to_nic(wdi);
	u64 ns, cyc2, cyc3;

	/*
	 * This read will also flush posted PCI writes, if any, and "warm up"
	 * the PCI link.
	 */
	nic->irq_pending = irq_is_pending(nic);

	cyc2 = rdtsc_ordered();
	read32(nic, I210_SYSTIMR);
	cyc3 = rdtsc_ordered();

	/* Read the latched NIC time. */
	ns = read32(nic, I210_SYSTIML);
	ns += read32(nic, I210_SYSTIMH) * NSEC_PER_SEC;

	if (tdata[0].val == 0) {
		/*
		 * Save the warmup and latch delays in order to have them included in
		 * the trace output.
		 */
		tdata[0].val = cyc2 - cyc1;
		tdata[1].val = cyc3 - cyc2;
	}

	/*
	 * Ideally, time after idle is the time at the moment this function is
	 * entered. Therefore, the adjustment is the time spent reading the
	 * pending IRQs status, plus half of the time latch operation.
	 */
	*adj_cyc = (cyc2 - cyc1) + (cyc3 - cyc2)/2;
	return ns;
}

static int arm_irq(struct wult_device_info *wdi, u64 *ldist)
{
	struct network_adapter *nic = wdi_to_nic(wdi);
	unsigned long flags;
	struct timespec64 ts;
	u64 ns;

	tdata[0].val = 0;
	nic->irq_pending = false;

	preempt_disable();
	local_irq_save(flags);

	read32(nic, I210_SYSTIMR);
	ns = read32(nic, I210_SYSTIML);
	ns += read32(nic, I210_SYSTIMH) * NSEC_PER_SEC;

	nic->ltime = ns + *ldist;

	/* Program the interrupt time. */
	ts = ns_to_timespec64(nic->ltime);
	write32(nic, (u32)ts.tv_sec, I210_TRGTTIMH0);
	write32(nic, (u32)ts.tv_nsec, I210_TRGTTIML0);
	pci_flush_posted(nic);

	/* Trigger the delayed event (interrupt). */
	write32(nic, I210_TSAUXC_EN_TT0, I210_TSAUXC);

	local_irq_restore(flags);
	preempt_enable();

	return 0;
}

static bool event_has_happened(struct wult_device_info *wdi)
{

	struct network_adapter *nic = wdi_to_nic(wdi);

	return nic->irq_pending;
}

static u64 get_launch_time(struct wult_device_info *wdi)
{
	return wdi_to_nic(wdi)->ltime;
}

static struct wult_trace_data_info *get_trace_data(struct wult_device_info *wdi)
{
	return tdata;
}

/* Disable NIC bus master activities. */
static int bus_master_disable(const struct network_adapter *nic)
{
	int slept = 0;
	u32 reg;

	reg = read32(nic, I210_CTRL);
	write32(nic, reg | I210_CTRL_GIO_MASTER_DISABLE, I210_CTRL);

	/*
	 * Wait for the card to indicate that all pending bus master activities
	 * have been finished.
	 */
	do {
		if (!(read32(nic, I210_STATUS) & I210_STATUS_GIO_MASTER_ENABLE))
			break;
		msleep(10);
		slept += 10;
	} while (slept < I210_BUS_MASTER_TIMEOUT);

	if (slept >= I210_BUS_MASTER_TIMEOUT) {
		wult_err("bus master disable failed");
		return -EINVAL;
	}

	return 0;
}

/* Mask all NIC interrupts */
static void mask_interrupts(const struct network_adapter *nic)
{
	write32(nic, I210_Ixx_VALID_BITS, I210_IMC);
	write32(nic, I210_EIxx_VALID_BITS, I210_EIMC);
	pci_flush_posted(nic);
}

/* Reset the NIC. */
static int nic_reset(const struct network_adapter *nic)
{
	int err, slept = 0;
	u32 reg, mask;

	wult_dbg("resetting the device");

	mask_interrupts(nic);

	/* Disable bus mastering. */
	err = bus_master_disable(nic);
	if (err)
		return err;

	reg = read32(nic, I210_CTRL);
	write32(nic, reg | I210_CTRL_RST, I210_CTRL);

	/*
	 * According to I210 datasheet we should not access NIC registers for at
	 * least 3 milliseconds after software reset.
	 */
	usleep_range(3000, 5000);
	slept += 3;

	/* Disable interrupts again as the datasheed suggests. */
	mask_interrupts(nic);

	/* Wait for the NIC to be done with reading its flash memory. */
	do {
		if (read32(nic, I210_EEC) & I210_EEC_AUTO_RD)
			break;
		msleep(10);
		slept += 10;
	} while (slept < I210_RESET_TIMEOUT);

	if (slept >= I210_RESET_TIMEOUT) {
		wult_err("NIC software reset failed: I210_EEC_AUTO_RD bit");
		return -EINVAL;
	}

	/* Check various bits as it is required by the HW specification. */
	reg = read32(nic, I210_STATUS);
	if (!(reg | I210_STATUS_PF_RST_DONE)) {
		wult_err("NIC software reset failed: I210_STATUS_PF_RST_DONE bit");
		return -EINVAL;
	}
	reg = read32(nic, I210_EEMNGCTL);
	if (!(reg | I210_EEMNGCTL_CFG_DONE)) {
		wult_err("NIC software reset failed: I210_EEMNGCTL_CFG_DONE bit");
		return -EINVAL;
	}

	/* Check error indication bits. */
	reg = read32(nic, I210_FWSM);
	mask = I210_FWSM_EXT_ERR_IND | I210_FWSM_PCIE_CONFIG_ERR_IND |
	       I210_FWSM_PHY_SERDES0_CONFIG_ERR_IND;
	if (reg & mask) {
		wult_err("NIC software reset failed: error indication bit(s) in FWSM register: %#x",
			 reg);
		return -EINVAL;
	}

	return 0;
}

static void hw_init(struct network_adapter *nic)
{
	/* Enable the system timer. */
	write32(nic, I210_TSAUXC_EN_TT0, I210_TSAUXC);

	/* Ensure the interrupt conditions are cleared */
	read32(nic, I210_ICR);
	read32(nic, I210_EICR);
	read32(nic, I210_TSICR);

	/* Enable the interrupts that we are giong to use. */
	write32(nic, I210_Ixx_TIME_SYNC, I210_IMS);
	write32(nic, I210_TSIxx_TT0, I210_TSIM);
	write32(nic, I210_EIxx_OTHER, I210_EIMS);
}

static int init_device(struct wult_device_info *wdi, int cpunum)
{
	struct network_adapter *nic = wdi_to_nic(wdi);
	int err, vector;

	err = nic_reset(nic);
	if (err)
		return err;

	hw_init(nic);

	err = pci_alloc_irq_vectors(nic->pdev, 1, 1, PCI_IRQ_ALL_TYPES);
	if (err < 0)
		goto err_master;

	vector = pci_irq_vector(nic->pdev, 0);

#ifdef COMPAT_HAVE_SET_AFFINITY
	err = irq_set_affinity(vector, get_cpu_mask(cpunum));
#else
	err = irq_set_affinity_hint(vector, get_cpu_mask(cpunum));
#endif
	if (err)
		goto err_irq;

	err = request_irq(vector, interrupt_handler, 0, DRIVER_NAME, nic);
	if (err)
		goto err_vecs;

	return 0;

err_irq:
	free_irq(vector, nic);
err_vecs:
	pci_free_irq_vectors(nic->pdev);
err_master:
	bus_master_disable(nic);
	return err;
}

static void exit_device(struct wult_device_info *wdi)
{
	struct network_adapter *nic = wdi_to_nic(wdi);
	int vector;

	mask_interrupts(nic);
	bus_master_disable(nic);
	vector = pci_irq_vector(nic->pdev, 0);
	free_irq(vector, nic);
	pci_free_irq_vectors(nic->pdev);
}

static const struct wult_device_ops wult_igb_ops = {
	.get_time_before_idle = get_time_before_idle,
	.get_time_after_idle = get_time_after_idle,
	.arm = arm_irq,
	.event_has_happened = event_has_happened,
	.get_launch_time = get_launch_time,
	.get_trace_data = get_trace_data,
	.init = init_device,
	.exit = exit_device,
};

static int pci_probe(struct pci_dev *pdev, const struct pci_device_id *id)
{
	struct network_adapter *nic;
	int err;

	nic = kzalloc(sizeof(struct network_adapter), GFP_KERNEL);
	if (!nic)
		return -ENOMEM;

	err = pci_enable_device_mem(pdev);
	if (err)
		goto err_free;

	err = dma_set_mask_and_coherent(&pdev->dev, DMA_BIT_MASK(64));
	if (err)
		goto err_disable_device;

	err = pci_request_mem_regions(pdev, DRIVER_NAME);
	if (err)
		goto err_disable_device;

	pci_set_master(pdev);
	pci_set_drvdata(pdev, nic);

	nic->pdev = pdev;
	nic->iomem = pci_iomap(pdev, 0, 0);
	if (!nic->iomem) {
		err = -ENODEV;
		goto err_clear_master;
	}

	nic->wdi.ldist_min = 1;
	nic->wdi.ldist_max = I210_MAX_LDIST;
	nic->wdi.ldist_gran = I210_RESOLUTION;
	nic->wdi.ops = &wult_igb_ops;
	nic->wdi.devname = DRIVER_NAME;

	err = wult_register(&nic->wdi);
	if (err)
		goto err_iounmap;

	return 0;

err_iounmap:
	iounmap(pdev);
err_clear_master:
	pci_clear_master(pdev);
	pci_release_mem_regions(pdev);
err_disable_device:
	pci_disable_device(pdev);
err_free:
	kfree(nic);
	return err;
}

static void pci_remove(struct pci_dev *pdev)
{
	struct network_adapter *nic = pci_get_drvdata(pdev);

	wult_unregister();
	iounmap(pdev);
	pci_clear_master(pdev);
	pci_release_mem_regions(pdev);
	pci_disable_device(pdev);
	kfree(nic);
}

static const struct pci_device_id pci_ids[] = {
	{ PCI_VDEVICE(INTEL, I210_PCI_ID_FIBER), },
	{ PCI_VDEVICE(INTEL, I210_PCI_ID_SERDES), },
	{ PCI_VDEVICE(INTEL, I210_PCI_ID_SGMII), },
	{ PCI_VDEVICE(INTEL, I211_PCI_ID_COPPER), },
	{ PCI_VDEVICE(INTEL, I210_PCI_ID_COPPER), },
	{ PCI_VDEVICE(INTEL, I210_PCI_ID_COPPER_FLASHLESS), },
	{ PCI_VDEVICE(INTEL, I210_PCI_ID_SERDES_FLASHLESS), },
	{ }
};
MODULE_DEVICE_TABLE(pci, pci_ids);

static struct pci_driver pci_driver = {
	.name = DRIVER_NAME,
	.id_table = pci_ids,
	.probe = pci_probe,
	.remove = pci_remove,
};
module_pci_driver(pci_driver);

MODULE_VERSION(WULT_VERSION);
MODULE_DESCRIPTION("Wult driver for Intel Gigabit Ethernet controllers.");
MODULE_AUTHOR("Artem Bityutskiy");
MODULE_LICENSE("GPL v2");
