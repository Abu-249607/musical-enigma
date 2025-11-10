#!/bin/bash

# Create Xcode project structure
mkdir -p TherapistMe.xcodeproj
mkdir -p TherapistMe.xcodeproj/project.xcworkspace
mkdir -p TherapistMe.xcodeproj/xcuserdata

# Create project.pbxproj (simplified)
cat > TherapistMe.xcodeproj/project.pbxproj << 'PBXPROJ'
// !$*UTF8*$!
{
	archiveVersion = 1;
	classes = {
	};
	objectVersion = 56;
	objects = {
		productName = TherapistMe;
		productReference = TherapistMe.app;
		productType = "com.apple.product-type.application";
	};
	rootObject = "Project object";
}
PBXPROJ

# Create workspace data
cat > TherapistMe.xcodeproj/project.xcworkspace/contents.xcworkspacedata << 'WORKSPACE'
<?xml version="1.0" encoding="UTF-8"?>
<Workspace
   version = "1.0">
   <FileRef
      location = "self:">
   </FileRef>
</Workspace>
WORKSPACE

echo "✅ Xcode project structure created!"
echo ""
echo "To open in Xcode:"
echo "1. Transfer this folder to your Mac"
echo "2. Double-click TherapistMe.xcodeproj"
echo "3. Add source files from TherapistMe/TherapistMe/"
