import numpy as np

'''fast check of the results by simple comparison of the maximum amplitude of the sismograms compared to the reference solution'''

def compute_error(sismo_name, threslhold):
    # read reference sismograms
    ux_ref=np.loadtxt('REF_SOLUTION/XX.'+sismo_name+'.CXX.semd')
    uy_ref=np.loadtxt('REF_SOLUTION/XX.'+sismo_name+'.CXY.semd')
    uz_ref=np.loadtxt('REF_SOLUTION/XX.'+sismo_name+'.CXZ.semd')

    # read sismograms
    ux=np.loadtxt('OUTPUT_FILES/XX.'+sismo_name+'.CXX.semd')
    uy=np.loadtxt('OUTPUT_FILES/XX.'+sismo_name+'.CXY.semd')
    uz=np.loadtxt('OUTPUT_FILES/XX.'+sismo_name+'.CXZ.semd')   


    # compute maximum amplitude
    max_ux_ref=max(abs(ux_ref[:,1]))
    max_uy_ref=max(abs(uy_ref[:,1]))
    max_uz_ref=max(abs(uz_ref[:,1]))

    max_ref = max(max_ux_ref,max_uy_ref,max_uz_ref)

    max_ux=max(abs(ux[:,1]))
    max_uy=max(abs(uy[:,1]))
    max_uz=max(abs(uz[:,1]))

    max_sol = max(max_ux,max_uy,max_uz)

    # compute the error
    error_max = np.abs(max_ref-max_sol)/max_ref

    if (error_max > threslhold):
        print('Checking ' + sismo_name +' WARNING  : max relative error too big  : ',error_max)
    else:
        print('Checking ' + sismo_name + ' OK : max relative error under the  threslhold : ',error_max)
   
# threslhold for the error (GPU computation is in single precision)
threslhold = 1e-5
print('Threslhold for the error : ',threslhold)
# list of sismograms to check
sismos = ['STA0010', 'STA0020', 'STA0040', 'STA0050', 'STA0075']

for sismo in sismos:
    compute_error(sismo, threslhold)