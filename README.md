# test_camer_triggers_fusion
## Steps to reproduce
0. Use the dynamic addin structure (trigger custom event -> custom event pus function into queue and triggers command --> command executes everything in the queue)
1. Register a custom event in the command created handler, the custom event handler puts a function into the execution queue which updates the current camera and calls the command.doExecute(FAlse) method.
2. implement a integer spinner input in the created handler
3. trigger the custom event in the input changed handler

## Problem / Effect
The input_Changed handler gets called twice at a input change and also the integer spinner increases or decreses by two values instead of one.

## Exspected behaviour
The inpur changed handler should only be called once as this is the case if we do something else like building a cube and not change the camera.