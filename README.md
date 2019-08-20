# PrusaFusion
PrusaSlicer Plugin over network (SSH) for Fusion 360 

Easily push Fusion 360 designs to another machine from within Fusion 360 and instantly start slicing!

![PrusaFusion Cover](./Resources/PrusaFusion_Cover.png)

## Current platform support:
- Linux

## Use cases:

1. From Fusion VM to Linux Host

2. From Fusion PC to Linux Laptop connected to the 3d Printer

3. From Fusion PC to Raspberry Pi connected to the Printer

4. ....

## Info:

Stl are in the tmp directories on both Platforms.

There are two components. The sender aka Fusion plugin and the reciver aka prusafusion_daemon.sh and fusion_helper.sh

## Usage:
First see [How to install sample Add-Ins and Scripts](https://rawgit.com/AutodeskFusion360/AutodeskFusion360.github.io/master/Installation.html)

Basic usage:
  * Install in Windows
  * Connect one time with pscp.exe and plink.exe to the host to safe the ssh key in the registry
  * prusafusion_daemon.sh and fusion_helper.sh go to ~.PrusaSlicer, make them executeable.
  * Make sure prusafusion_daemon.sh is running from a Linux user.
  * Change PATH Variable in prusafusion_daemon.sh to the correct one for your PrusaSlicer.AppImage
  * Export a Design in Fusion and start slicing.

## Not implemented:
- Some weird nameing like { } but this is possible: Ärmüden Überstößel Öberkärper[ruschä Version] (11.2) v1.stl

## License
Licensed under the terms of the [MIT License](http://opensource.org/licenses/MIT). Please see the [LICENSE](LICENSE) file for full details.

## Written by

me

Fork from https://github.com/tapnair/OctoFusion, heavily modified.
