# Android Image Tool — User Guide

![App icon](../assets/logo.png)

## What it is

Android Image Tool is a Windows, Linux, and macOS utility for inspecting and preparing Android partition images for custom-ROM development. It never flashes a device automatically and does not edit source images in place.

## Typical workflow

1. Open a stock image and inspect its detected format.
2. Create a project copy and record SHA-256 values.
3. Extract an ext4 filesystem or boot ramdisk.
4. Edit files such as `init`, `fstab`, or vendor logo data.
5. Rebuild to a new output file.
6. Run `validate` and compare the output against the original.
7. Verify AVB/signing and device compatibility before flashing with your own trusted workflow.

## External tools

The GUI asks before obtaining missing tools. Google Platform-Tools are downloaded only after confirmation from Google's official URL. For `avbtool`, `mkbootimg`, `lpunpack`, `mkfs.erofs`, and payload tools, the application opens upstream instructions rather than silently executing an unknown binary.

## Localization

Edit `locales/en.json` or `locales/ja.json`, then restart the app. The JSON files are the source of UI text.
