import os,sys,fnmatch

# templateDir='/user_data/jhogan/CMSSW_7_4_14/src/tptp_2016/makeTemplates/'
templateDir='/home/rsyarif/LJMet/TprimeAnalysis/CMSSW_7_6_3/src/SingleLep_XCone/singleLepAnalyzer/makeTemplates/'
#templateDir+='templates_minMlb_2016_9_3' #Total number of jobs submitted: 54432
# templateDir+='templates4CRhtSR_NewEl' #Total number of jobs submitted: 14040
# templateDir+='templates_NewEl_2018_2_8' #Total number of jobs submitted: 14040
# templateDir+='templates_NewEl_2018_2_12' #Total number of jobs submitted: 14040
# templateDir+='templates_NewEl_BB_2018_3_12' #Total number of jobs submitted: 14040
# templateDir+='templates_NewEl_2018_3_22' #minMlbNXConeJetsST, minMlbNXConeJets
# templateDir+='templates_NewEl_2018_3_27' #minMlbNXConeJetsV2, ST
# templateDir+='templates_rizki_SR_GlobalNX5p_2018_4_16' 
templateDir+='templates_rizki_SR_NewXConeCat_2018_4_16' 
thetaConfigTemp = os.getcwd()+'/theta_config_template.py'
#thetaConfigTemp = os.getcwd()+'/theta_discovery.py'
fileDir = 'splitLess'
# fileDir = 'splitLess/binning_v1' #binning not optimal

# systematicsInFile = ['pileup','muRFcorrd','muR','muF','toppt','jsf','topsf','jmr','jms','tau21','btag','mistag','jer','jec','q2','pdfNew','muRFcorrdNew']#,'btagCorr']
systematicsInFile = ['pileup','muRFcorrd','muR','muF','toppt','jsf','topsf','jmr','jms','tau21','btag','mistag','q2','pdfNew','muRFcorrdNew']#,'btagCorr']
cats = ['isE_nT0_nW0_nB0', 'isE_nT0_nW0_nB1', 'isE_nT0_nW0_nB2p', 'isE_nT0_nW1p_nB0', 'isE_nT0_nW1p_nB1', 'isE_nT0_nW1p_nB2p',
        'isE_nT1p_nW0_nB0','isE_nT1p_nW0_nB1','isE_nT1p_nW0_nB2p','isE_nT1p_nW1p_nB0','isE_nT1p_nW1p_nB1','isE_nT1p_nW1p_nB2p',
        'isM_nT0_nW0_nB0', 'isM_nT0_nW0_nB1', 'isM_nT0_nW0_nB2p', 'isM_nT0_nW1p_nB0', 'isM_nT0_nW1p_nB1', 'isM_nT0_nW1p_nB2p',
        'isM_nT1p_nW0_nB0','isM_nT1p_nW0_nB1','isM_nT1p_nW0_nB2p','isM_nT1p_nW1p_nB0','isM_nT1p_nW1p_nB1','isM_nT1p_nW1p_nB2p',
        ]
# toFilter0 = ['toppt','_nH1p_nW0p_nB0_isCR']#'pdf','muRFdecorrdNew','muRFenv','muR','muF','muRFcorrd'] #always remove in case they are in templates
toFilter0 = ['toppt','_nH1p_nW0p_nB0_isCR','_nB0_isSR' ]#'pdf','muRFdecorrdNew','muRFenv','muR','muF','muRFcorrd'] #always remove in case they are in templates
#toFilter0+= ['topsf','jsf']
#toFilter0+= ['jsf']
#toFilter0+= ['topsf']
#toFilter0 = systematicsInFile
toFilter0 = [item for item in toFilter0]

limitConfs = {#'<limit type>':[filter list]
# 	'minMlbNXConeJetsST':[],
# 	'minMlbNXConeJets':[],
# 	'minMlbNXConeJetsV2':[],
    #'NXConeJetsST':[],
    #'NXConeJets':[],
#     'maxMlep3XConeJetsST':[],
#     'maxMlep3XConeJets':[],
    'STminMlb':[],
#     'minMlbST':[],
    #'minMlb':[],
#     'ST':[],
    #'deltaRAK8':[]
# 			  'isE':['isM'], #only electron channel
# 			  'isM':['isE'], #only muon channel
# 			  'nT0':['nT1p'], #only 0 t tag category
# 			  'nT1p':['nT0'], #only 1p t tag category
# 			  'nW0':['nW1p'], #only 0 W tag category
# 			  'nW1p':['nW0'], #only 1p W tag category
# 			  'nB0':['nB1','nB2p'], #only 0 b tag category
# 			  'nB1':['nB0','nB2p'], #only 1 b tag category
# 			  'nB2p':['nB0','nB1'], #only 2p b tag category
# 			  'noB0':['nB0'], #No 0 b tag category
			  #'no_nT0_nW0_nB0':['nT0_nW0_nB0'],
			  }
# limitConfs = {}
# for cat in cats: 
# 	limitConfs[cat] = []
# 	for cat2 in cats:
# 		if cat2!=cat: limitConfs[cat].append(cat2)

#os._exit(1)
#limitType = 'noCRHB0'#DRJetCR'#'noSysts'
# limitType = 'SRNoB0_binnning_v1'#DRJetCR'#'noSysts'
# limitType = 'SRNoB0_binnning_v2'#DRJetCR'#'noSysts'
# limitType = 'SRNoB0' 
# limitType = 'SRNoB0_GlobalNX5p' 
limitType = 'SRNoB0_NewXConeCat' 
# outputDir = os.getcwd()+'/limitsAug17/'+templateDir.split('/')[-1]+'/' #prevent writing these (they are large) to brux6 common area
outputDir = '/user_data/rsyarif/singleLepXConelimits/'+templateDir.split('/')[-1]+'/' #prevent writing these (they are large) to brux6 common area
if not os.path.exists(outputDir): os.system('mkdir -vp '+outputDir)
outputDir+= '/'+limitType+'/'
if not os.path.exists(outputDir): os.system('mkdir -vp '+outputDir)
print outputDir

def findfiles(path, filtre):
    for root, dirs, files in os.walk(path):
        for f in fnmatch.filter(files, filtre):
            yield os.path.join(root, f)
            
rootfilelist = []
i=0
for rootfile in findfiles(templateDir, '*.root'):
    #if 'lep50_MET150_NJets4_NBJets0_DR1_1jet450_2jet150_3jet0' not in rootfile: continue
    if 'splitLess' not in rootfile:continue
    if 'binning_v1' in rootfile:continue
    if 'BKGNORM_rebinned_stat0p3.root' not in rootfile: continue
    if 'plots' in rootfile: continue
    if 'bW' not in rootfile: continue
#     if not ('0p5' in rootfile): continue
#     if not ('bW0p5' in rootfile or 'bW0p0' in rootfile): continue
    if not ('bW1p0' in rootfile or 'tZ1p0' in rootfile or 'tH1p0' in rootfile): continue
#     if 'tW' not in rootfile: continue
#     if not ('0p5' in rootfile): continue
#     if not ('tW0p5' in rootfile or 'tW0p0' in rootfile): continue
#     if not ('tW1p0' in rootfile or 'bZ1p0' in rootfile or 'bH1p0' in rootfile): continue
    #if 'tZ0p5_tH1p0' in rootfile: continue
    #if '0p5' not in rootfile and 'W1p0' not in rootfile and 'H1p0' not in rootfile: continue
    print "ADDING file : ", rootfile
    rootfilelist.append(rootfile)
    i+=1

f = open(thetaConfigTemp, 'rU')
thetaConfigLines = f.readlines()
f.close()

def makeThetaConfig(rFile,outDir):
	#rFileDir = rFile.split('/')[-2]
        rFileDir = fileDir
	with open(outDir+'/'+rFileDir+'/'+rFile.split('/')[-1][:-5]+'.py','w') as fout:
		for line in thetaConfigLines:
			if line.startswith('outDir ='): fout.write('outDir = \''+outDir+'/'+rFileDir+'\'')
			elif line.startswith('input ='): fout.write('input = \''+rFile+'\'')
			elif line.startswith('    model = build_model_from_rootfile('): 
				if len(toFilter)!=0:
					model='    model = build_model_from_rootfile(input,include_mc_uncertainties=True,histogram_filter = (lambda s:  s.count(\''+toFilter[0]+'\')==0'
					for item in toFilter: 
						if item!=toFilter[0]: model+=' and s.count(\''+item+'\')==0'
					model+='))'
					fout.write(model)
				else: fout.write(line)
			else: fout.write(line)
	with open(outDir+'/'+rFileDir+'/'+rFile.split('/')[-1][:-5]+'.sh','w') as fout:
		fout.write('#!/bin/sh \n')
		fout.write('cd /home/ssagir/CMSSW_7_3_0/src/\n')
		fout.write('source /cvmfs/cms.cern.ch/cmsset_default.sh\n')
		fout.write('cmsenv\n')
		fout.write('cd '+outDir+'/'+rFileDir+'\n')
		fout.write('/home/ssagir/CMSSW_7_3_0/src/theta/utils2/theta-auto.py ' + outDir+'/'+rFileDir+'/'+rFile.split('/')[-1][:-5]+'.py')

count=0
for limitConf in limitConfs:
	toFilter = toFilter0 + limitConfs[limitConf]
	print limitConf,'=',toFilter
	for file in rootfilelist:
                if '_'+limitConf+'_' not in file: continue
		fileName = file.split('/')[-1]
		signal = fileName.split('_')[2]
		BRStr = fileName[fileName.find(signal)+len(signal):fileName.find('_36p814fb')]
		outDir = outputDir+limitConf+BRStr+'/'
		print signal,BRStr,fileName
		if not os.path.exists(outDir): os.system('mkdir -vp '+outDir)
		os.chdir(outDir)
		#fileDir = file.split('/')[-2]
		if not os.path.exists(outDir+fileDir): os.system('mkdir -vp '+fileDir)
		os.chdir(fileDir)
		makeThetaConfig(file,outDir)

		dict={'configdir':outDir+fileDir,'configfile':file.split('/')[-1][:-5]}

		jdf=open(file.split('/')[-1][:-5]+'.job','w')
		jdf.write(
"""universe = vanilla
Executable = %(configfile)s.sh
Should_Transfer_Files = YES
WhenToTransferOutput = ON_EXIT
Notification = Error
request_memory = 3072

arguments      = ""

Output = %(configfile)s.out
Error = %(configfile)s.err
Log = %(configfile)s.log

Queue 1"""%dict)
		jdf.close()

		os.system('chmod +x '+file.split('/')[-1][:-5]+'.sh')
		os.system('condor_submit '+file.split('/')[-1][:-5]+'.job')
		os.chdir('..')
		count+=1
print "Total number of jobs submitted:", count
                  
