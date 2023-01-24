#!/bin/bash

bluetoothctl
wait ${!}
bluetoothctl -- scan on 
wait ${!}
exit