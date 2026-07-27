---
id: 01JEV000000000000000000082
title: Field Wi-Fi Access Point Notes
aliases: []
type: configuration
created: 2024-01-01T09:00:00Z
updated: 2024-04-06T12:00:00Z
tags: [infrastructure, networking]
---
# Field Wi-Fi Access Point Notes

## Placement and Channel Configuration

The field-office Wi-Fi access point (Ubiquiti UniFi 6E model) is mounted on the east corner of the main shelter, approximately 2.8 m above ground level. This elevation provides adequate coverage across the outdoor equipment area and the vehicle parking zone while maintaining distance from the primary satellite dish to avoid RF interference.

**Current configuration:**
- 2.4 GHz band: Channel 6, 20 MHz width, max transmit power 20 dBm
- 5 GHz band: Channel 36 (UNII-1), 80 MHz width, max transmit power 23 dBm
- 6 GHz band: Channel 21 (6105 MHz), 160 MHz width, max transmit power 24 dBm

The 2.4 GHz channel was chosen to minimize overlap with the adjacent site's infrastructure on Channels 1 and 11. Performance remains stable despite site-to-site propagation at approximately 4.2 km distance.

## Environmental Considerations and Weatherproofing

The antenna assembly is enclosed in a [[Weatherproof Enclosure Standards|rated IP67 enclosure]] with protective foam padding around cable glands. All connections use stainless-steel connectors rated for maritime environments. The mounting bracket includes strain relief for the CAT6a backbone cable running to the equipment cabinet.

Adjacent infrastructure including the [[Lightning Protection Notes|surge arrestor protection]] requires careful cable routing to avoid creating ground loops. The access point undergoes quarterly inspection for salt spray corrosion, particularly at connector interfaces.

## Integration with Field Systems

This Wi-Fi deployment operates independently from the station's primary network tunnel; it provides temporary connectivity for field technicians during maintenance windows and site surveys. Access credentials are rotated per the facility's security policy and are distinct from permanent infrastructure accounts.

Failover behavior remains untested in regular operations—refer to [[Backup Internet Failover Test]] results for scenarios involving loss of the primary internet feed. The [[Firmware Update Log - Router|router firmware cycle]] includes periodic security patches that may affect bridge stability when Wi-Fi is active.

## Related Infrastructure Notes

- [[Remote Access Audit 2025]]
- [[Battery Bank Maintenance Log]]
- [[DNS and Hostnames]]
