# FAQ

## Does editing a ramdisk edit the boot image?

No. The ramdisk is unpacked and repacked as a separate component. Use a compatible `mkbootimg` workflow to rebuild the complete boot image, then verify AVB metadata before flashing.

## Why was a tool not downloaded automatically?

Executing an unverified binary is unsafe. The app downloads Platform-Tools only from Google's official distribution after confirmation. Other tools require the user to review and install the upstream project.

## Can it flash my phone?

No automatic flashing is provided. The tool focuses on inspection, backups, logs, validation, and safe output generation.
