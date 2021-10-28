// SPDX-License-Identifier: GPL-2.0-only
/*
 * Copyright (C) 2019-2021 Intel Corporation
 * Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>
 */

#ifndef _WULT_IGB_H_
#define _WULT_IGB_H_

#include <linux/atomic.h>
#include <linux/bits.h>
#include <linux/kernel.h>
#include <asm/io.h>
#include "wult.h"

/* Device Status Register. */
#define I210_STATUS 0x0008
/* The 'Reset Done' bit. */
#define I210_STATUS_PF_RST_DONE BIT(21)
/* The 'GIO Master Enable Status' bit. */
#define I210_STATUS_GIO_MASTER_ENABLE BIT(19)

/* Device Control Register. */
#define I210_CTRL 0x0000
/* The 'GIO Master Disable' bit. */
#define I210_CTRL_GIO_MASTER_DISABLE BIT(2)
/* The 'Software Reset' bit. */
#define I210_CTRL_RST BIT(26)
/* The 'Device Reset' bit. */
#define I210_CTRL_DEV_RST BIT(29)

/* EEPROM Mode Control Register. */
#define I210_EEC 0x12010
/* The 'Flash Auto-Read Done' bit. */
#define I210_EEC_AUTO_RD BIT(9)

/* Interrupt Cause Read Register. */
#define I210_ICR 0x1500
/* Interrupt Cause Set Register. */
#define I210_ICS 0x1504
/* Interrupt Mask Clear Register. */
#define I210_IMC 0x150C
/* Interrupt Mask Set/Read Register. */
#define I210_IMS 0x1508
/* The 'Time_Sync Interrupt' bit. */
#define I210_Ixx_TIME_SYNC BIT(19)
/* Valid ICR register bits. */
#define I210_Ixx_VALID_BITS (GENMASK(30, 29) | GENMASK(26,24) | BIT(22) | \
			     GENMASK(19, 18) | GENMASK(14, 10) | \
			     GENMASK(7, 4) | BIT(2) | BIT(0))

/* Extended Interrupt Cause Register. */
#define I210_EICR 0x1580
/* Extended Interrupt Cause Set Register. */
#define I210_EICS 0x1520
/* Extended Interrupt Mask Clear Register. */
#define I210_EIMC 0x1528
/* Extended Interrupt Mask Set/Read Register. */
#define I210_EIMS 0x1524
/* The 'Other Cause' bit. */
#define I210_EIxx_OTHER BIT(31)
/* Valid EICR register bits. */
#define I210_EIxx_VALID_BITS (GENMASK(31, 30) | GENMASK(3, 0))

/* Time Sync Interrupt Cause Register. */
#define I210_TSICR 0xB66C
/* Time Sync Interrupt Masc Register. */
#define I210_TSIM 0xB674
/* The 'Target Time 0 Trigger' bit. */
#define I210_TSIxx_TT0 BIT(3)

/* System Time Residue Register. */
#define I210_SYSTIMR 0xB6F8
/* System Time Low Register. */
#define I210_SYSTIML 0xB600
/* System Time High Register. */
#define I210_SYSTIMH 0xB604
/* Target Time 0 Low Register. */
#define I210_TRGTTIML0 0xB644
/* Target Time 0 High Register. */
#define I210_TRGTTIMH0 0xB648

/* Time Sync Auxiliary Control Register. */
#define I210_TSAUXC 0xB640
/* The 'Enable Target Time 0' bit. */
#define I210_TSAUXC_EN_TT0 BIT(0)

/* The Managebility EEPROM-Mode Control Register. */
#define I210_EEMNGCTL 0x12030
/* The 'Manageability Configuration Cycle of the Port Completed' bit. */
#define I210_EEMNGCTL_CFG_DONE BIT(18)

/* The Firmware Semaphore Register. */
#define I210_FWSM 0x5B54
/* The 'External Error Indication' bits (24:19).*/
#define I210_FWSM_EXT_ERR_IND 0x1F80000
/* The 'PCIe Configuration Error Indication' bit. */
#define I210_FWSM_PCIE_CONFIG_ERR_IND BIT(25)
/* The 'PHY/SerDes Configuration Error Indication' bit. */
#define I210_FWSM_PHY_SERDES0_CONFIG_ERR_IND BIT(26)

/* Maximum supported launch distance (nanoseconds). */
#define I210_MAX_LDIST 10000000
/* The launch distance resolution (nanoseconds). */
#define I210_RESOLUTION 1

/* NIC reset timeout in milliseconds. */
#define I210_RESET_TIMEOUT 100
/* NIC bus master disable timeout milliseconds. */
#define I210_BUS_MASTER_TIMEOUT 100

/* PCI IDs of NICs supported by this driver. */
#define I210_PCI_ID_FIBER  0x1536
#define I210_PCI_ID_SERDES 0x1537
#define I210_PCI_ID_SGMII  0x1538
#define I210_PCI_ID_COPPER 0x1533
#define I211_PCI_ID_COPPER 0x1539
#define I210_PCI_ID_COPPER_FLASHLESS 0x157B
#define I210_PCI_ID_SERDES_FLASHLESS 0x157C

/*
 * Get a 'struct network_adapter' pointer by memory address of its 'wdi' field.
 */
#define wdi_to_nic(wdi) container_of(wdi, struct network_adapter, wdi)

struct pci_dev;

/*
 * TSC snapshots at various points of the measurement.
 */
struct wult_igb_cycles {
	/* TSC counter snapshots taken in 'get_time_before_idle()'. */
	u64 tbi1, tbi2, tbi3;
	/* TSC counter snapshots taken in 'get_time_after_idle()'. */
	u64 tai1, tai2, tai3;
};

/* This structure represents the NIC. */
struct network_adapter {
	struct wult_device_info wdi;
	struct pci_dev *pdev;
	u8 __iomem *iomem;
	/* Launch time of the last armed delayed event in nanoseconds. */
	u64 ltime;
	struct wult_igb_cycles cyc;
	bool irq_pending;
};

#endif
