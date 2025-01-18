# raikoke-2019-large


## Files 

- `FALL3D.gpu.cmd` - reference slurm script used by developers on Leonardo
- `FALL3D_GH200.inp` - see [docs](https://fall3d-suite.gitlab.io/fall3d/chapters/tasks.html#the-namelist-file)

## Information from developers

"We ran one hour test simulation on Leonardo using 4 nodes (16 GPUs), which took approximately 950 seconds. The input files are now configured for a 72 hour simulation. Since we are unsure how the code will perform on GH200 devices, you can easily adjust the simulation duration by modifying the input file "FALL3D_GH200.inp", in line 33 parameter "RUN_END_(HOURS_AFTER_00)="  to a value between 19 (1 hour simulation) and 90 (72 hour simulation)."

