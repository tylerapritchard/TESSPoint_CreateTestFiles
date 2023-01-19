import pandas as pd
import numpy as np
import subprocess

def testprod(data):
    dat=data
    a,b,c = dat
    return (a,b,c)

def create_test_array(ticlist,xlist,ylist,Sector, Camera, CCD):
    ra_return=[]
    dec_return=[]
    for tic, x, y in zip(ticlist, xlist, ylist):
        point=subprocess.run(["python","/Users/tapritc2/tessgi/tesspoint/tess-point/tess_stars2px.py",
                        "-r",str(Sector),str(Camera),str(CCD),str(x),str(y)],capture_output=True,text=True)
        ra_return.append(float(point.stdout.split(' ')[0]))
        dec_return.append(float(point.stdout.split(' ')[1]))
    return ticlist, ra_return, dec_return

def create_test_file(ticlist,xlist,ylist,Sector, Camera, CCD):
    tic, ra, dec = create_test_array(ticlist,xlist,ylist,Sector, Camera, CCD)
    f= open("testfiles/TEST_pix2radec_Sec{:02d}_Cam{}_CCD{}_stars2px.dat".format(Sector,Camera,CCD),'w')
    f.write('# TIC RA DEC \n')
    for t_out,ra_out,dec_out in zip (tic,ra, dec):
        f.write('{0} {1} {2} \n'.format(t_out,ra_out,dec_out))
    f.close()
    return

def multi_create_test_file(SectorCameraCCD):
    Sector, Camera, CCD = SectorCameraCCD
    footprint_file='footprint_input.dat'
    footprint_df=pd.read_csv(footprint_file,delimiter=' ',names=['tic','x','y'],index_col=False)
    create_test_file(footprint_df.tic.to_numpy(),footprint_df.x.to_numpy(),footprint_df.y.to_numpy(),
                     Sector, Camera, CCD)
    return True

def create_reverse_file(SectorCameraCCD):
    Sector, Camera, CCD = SectorCameraCCD
    wcsfile="testfiles/TEST_pix2radec_Sec{:02d}_Cam{}_CCD{}_stars2px.dat".format(Sector,Camera,CCD)
    pixfile="testfiles/TEST_radec2pix_Sec{:02d}_Cam{}_CCD{}_stars2px.dat".format(Sector,Camera,CCD)
    point=subprocess.run(["python","/Users/tapritc2/tessgi/tesspoint/tess-point/tess_stars2px.py",
                        "-s",str(Sector),"-f",wcsfile,"-o",pixfile],capture_output=True,text=True)
    return

def calc_deviation_scc(SectorCameraCCD):
    Sector, Camera, CCD = SectorCameraCCD
    
    pixfile="testfiles/TEST_radec2pix_Sec{:02d}_Cam{}_CCD{}_stars2px.dat".format(Sector,Camera,CCD)
    footprint_file='footprint_input.dat'
    
    footprint_df=pd.read_csv(footprint_file,delimiter=' ',names=['tic','x','y'],index_col=False)
    final_df=pd.read_csv(pixfile,names=['tic','ra','dec','el','ela','s','c','ccd','x','y','edge'],
                         index_col=0, skiprows=16,delimiter="|" )
    
    idx = final_df.index.intersection(footprint_df.index)
    dx=abs(final_df.loc[idx, 'x'] - footprint_df.loc[idx, 'x'])
    dy=abs(final_df.loc[idx, 'y'] - footprint_df.loc[idx, 'y'])
    return len(idx),np.median(dx), np.max(dx), np.std(dx), np.median(dy), np.max(dy), np.std(dy), Sector, Camera, CCD
