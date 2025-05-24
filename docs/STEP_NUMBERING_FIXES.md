# Command Wizard Step Numbering Fixes

## Issue Summary

During testing of the Command Wizard, we identified inconsistencies in how steps were numbered and displayed to users. Some steps showed clear step numbers (e.g., "Step 1: Query") while others did not include step numbers (e.g., "Instruction Template Selection" instead of "Step 4: Instruction Template Selection").

This inconsistency could cause confusion for users as they navigate through the wizard.

## Changes Made

We updated the following sections to ensure consistent step numbering throughout the wizard:

1. **Step 2: Configuration File Selection**
   - Updated the display in both the Rich UI and non-Rich UI versions to include the step number
   - Changed from: "Configuration File Selection" 
   - Changed to: "Step 2: Configuration File Selection"

2. **Step 4: Instruction Template Selection**
   - Updated the display in both the Rich UI and non-Rich UI versions to include the step number
   - Changed from: "Instruction Template Selection" 
   - Changed to: "Step 4: Instruction Template Selection"

3. **Step 9: Advanced Options**
   - Updated the display in both the Rich UI and non-Rich UI versions to include the step number
   - Changed from: "Advanced Options"
   - Changed to: "Step 9: Advanced Options"

## Current Step Structure

After these changes, the Command Wizard now has a consistent step numbering pattern:

1. Step 1: Query
2. Step 2: Select configuration file (optional)
3. Step 3: Domain Selection
4. Step 4: Instruction Template Selection
5. Step 5: Model Selection
6. Step 6: Variations
7. Step 7: Sampling Method
8. Step 8: Output Options
9. Step 9: Advanced Options

## Benefits

- **Improved User Experience**: Users can now clearly see which step they are on and understand the overall flow of the wizard.
- **Clearer Navigation**: The consistent numbering helps users understand their progress through the wizard.
- **Better Documentation**: Steps can be referenced by their numbers in documentation and support materials.

## Future Recommendations

1. **Consider Progress Indicators**: Adding a visual progress indicator showing which step the user is on out of the total number of steps would further enhance the user experience.
2. **Step Grouping**: Consider grouping related steps together or providing an option to skip certain steps for advanced users.
3. **Saved Settings**: Implement a way for users to save their settings and skip directly to specific steps in future sessions.

These changes align with the UX Enhancement Roadmap, particularly Step 1.2 (Parameter Context Improvements) and the upcoming Step 1.3 (Command Preview Enhancements).