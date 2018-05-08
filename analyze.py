#!/usr/bin/python
from ROOT import TH1D,TTree,TFile
from array import array
from numpy import linspace
from weights import *

"""
--This function will make kinematic plots for a given distribution for electron, muon channels and their combination
--Check the cuts below to make sure those are the desired full set of cuts!
--The applied weights are defined in "weights.py". Also, the additional weights (SFs, 
negative MC weights, ets) applied below should be checked!
"""

lumiStr = str(targetlumi/1000).replace('.','p') # 1/fb
def analyze(tTree,process,cutList,isotrig,doAllSys,doJetRwt,iPlot,plotDetails,category,region,isCategorized):
	print "*****"*20
	print "*****"*20
	print "DISTRIBUTION:", iPlot
	print "            -name in ljmet trees:", plotDetails[0]
	print "            -x-axis label is set to:", plotDetails[2]
	print "            -using the binning as:", plotDetails[1]
	plotTreeName=plotDetails[0]
	xbins=array('d', plotDetails[1])
	xAxisLabel=plotDetails[2]
	
	print "/////"*5
	print "PROCESSING: ", process
	print "/////"*5

	# Define categories
	isEM  = category['isEM']
	nHtag = category['nHtag']
	nWtag = category['nWtag']
	nbtag = category['nbtag']
	njets = category['njets']
	catStr = 'is'+isEM+'_nH'+nHtag+'_nW'+nWtag+'_nB'+nbtag+'_nJ'+njets

	# Define general cuts
	cut  = '(leptonPt_singleLepCalc > '+str(cutList['lepPtCut'])+')'
	cut += ' && (corr_met_singleLepCalc > '+str(cutList['metCut'])+')'
	cut += ' && (theJetPt_JetSubCalc_PtOrdered[0] > '+str(cutList['jet1PtCut'])+')'
	cut += ' && (theJetPt_JetSubCalc_PtOrdered[1] > '+str(cutList['jet2PtCut'])+')'
	cut += ' && (theJetPt_JetSubCalc_PtOrdered[2] > '+str(cutList['jet3PtCut'])+')'
	cut += ' && (minDR_lepJet > 0.4 || ptRel_lepJet > 40)'
	if 'CR' in region:
		#cut += ' && (deltaR_lepJets[1] >= 0.4 && deltaR_lepJets[1] < '+str(cutList['drCut'])+')'
		cut += ' && (NJetsAK8_JetSubCalc >= 2) && (minDR_leadAK8otherAK8 >= '+str(cutList['drCut'])+')'
	else: # 'PS' or 'SR'
		#cut += ' && (deltaR_lepJets[1] >= '+str(cutList['drCut'])+')'
		if 'SR' in region: cut += ' && (NJetsAK8_JetSubCalc >= 2) && (minDR_leadAK8otherAK8 > 0.8 && minDR_leadAK8otherAK8 < '+str(cutList['drCut'])+')'		
		if 'NoB0' in region: cut += ' && NJetsCSVwithSF_JetSubCalc >= 1'
		if region=='PS2b': cut += ' && NJetsCSVwithSF_JetSubCalc >= 2'
		elif region=='PS1b': cut += ' && NJetsCSVwithSF_JetSubCalc >= 1'
		elif region=='PS0b': cut += ' && NJetsCSVwithSF_JetSubCalc == 0'
		#cut += ' && NXConeJets>=5' # added by rizki for SR_NX5Global Apr16-2018

	# Define weights
	TrigEff = 'TrigEffWeightRMA'
	TrigEffUp = 'min(1.0,TrigEffWeightRMA+TrigEffWeightRMAUncert)'
	TrigEffDn = '(TrigEffWeightRMA-TrigEffWeightRMAUncert)'
	if isotrig == 1:
		cut += ' && DataPastTriggerOR == 1' # && MCPastTrigger == 1' # no MC HLT except signal
	else:
		TrigEff = 'TrigEffAltWeight'
		cut += ' && DataPastTriggerAlt == 1' # && MCPastTriggerAlt == 1'

	jetSFstr='1'
	jetSFstrUp = '1'
	jetSFstrDn = '1'
	if (process!='WJetsMG' and 'WJetsMG' in process):
		if doJetRwt: 
			jetSFstr= 'JetSF_80X'
			jetSFstrUp = '1'
			jetSFstrDn = 'JetSF_80X*JetSF_80X'
		else: 
			jetSFstr = 'HTSF_Pol'
			jetSFstrUp = 'HTSF_PolUp'
			jetSFstrDn = 'HTSF_PolDn'
		#jetSFstr = str(genHTweight[process])

	weightStr = '1'
	if 'Data' not in process: 
		weightStr          += ' * '+jetSFstr+' * '+TrigEff+' * pileupWeight * isoSF * lepIdSF * EGammaGsfSF * MuTrkSF * (MCWeight_singleLepCalc/abs(MCWeight_singleLepCalc)) * '+str(weight[process])
		if 'TTJets' in process: weightStr = 'topPtWeight13TeV * '+weightStr
		weightTrigEffUpStr  = weightStr.replace(TrigEff,TrigEffUp)
		weightTrigEffDownStr= weightStr.replace(TrigEff,TrigEffDn)
		weightPileupUpStr   = weightStr.replace('pileupWeight','pileupWeightUp')
		weightPileupDownStr = weightStr.replace('pileupWeight','pileupWeightDown')
		weightmuRFcorrdUpStr   = 'renormWeights[5] * '+weightStr
		weightmuRFcorrdDownStr = 'renormWeights[3] * '+weightStr
		weightmuRUpStr      = 'renormWeights[4] * '+weightStr
		weightmuRDownStr    = 'renormWeights[2] * '+weightStr
		weightmuFUpStr      = 'renormWeights[1] * '+weightStr
		weightmuFDownStr    = 'renormWeights[0] * '+weightStr
		weighttopptUpStr    = weightStr.replace('topPtWeight13TeV','1')
		weighttopptDownStr  = weightStr.replace('topPtWeight13TeV','topPtWeight13TeV*topPtWeight13TeV')
		weightjsfUpStr      = weightStr.replace(jetSFstr,jetSFstrUp)
		weightjsfDownStr    = weightStr.replace(jetSFstr,jetSFstrDn)

	# For N-1 tagging cuts
	pt_var = 'theJetAK8Pt_JetSubCalc_PtOrdered'
	pruned_massvar = 'theJetAK8PrunedMassWtagUncerts_JetSubCalc_PtOrdered'
	soft_massvar='theJetAK8SoftDropMass_JetSubCalc_PtOrdered'
	puppi_massvar='theJetAK8PUPPISoftDrop_PtOrdered'
	nsubsvar = 'theJetAK8SDSubjetNCSVM_PtOrdered'
	puppitau21var = 'theJetAK8PUPPITau2_JetSubCalc_PtOrdered/theJetAK8PUPPITau1_JetSubCalc_PtOrdered'
	tau21var = 'theJetAK8NjettinessTau2_JetSubCalc_PtOrdered/theJetAK8NjettinessTau1_JetSubCalc_PtOrdered'
	tau32var = 'theJetAK8NjettinessTau3_JetSubCalc_PtOrdered/theJetAK8NjettinessTau2_JetSubCalc_PtOrdered'
	if 'PrunedWNm1' in iPlot: cut += ' && ('+tau21var+' < 0.6 && '+pt_var+' > 200)'
	if 'Tau21Nm1' in iPlot:  cut += ' && ('+pruned_massvar+' > 65 && '+pruned_massvar+' < 105 && '+pt_var+' > 200)'
	if 'PrunedHNm1' in iPlot: cut += ' && ('+nsubsvar+' > 1 && '+pt_var+' > 300)'
	if 'PrunedNsubBNm1' in iPlot: cut += ' && ('+pruned_massvar+' > 60 && '+pruned_massvar+' < 160 && '+pt_var+' > 300)'

	if 'SoftDropHNm1' in iPlot: cut+=  ' && ('+nsubsvar+' > 1 && '+pt_var+' > 300)'
	if 'SoftDropNsubBNm1' in iPlot: cut += ' && ('+soft_massvar+' > 60 && '+soft_massvar+' < 160 && '+pt_var+' > 300)'
	if 'SoftDropTNm1' in iPlot: cut+=  ' && ('+tau32var+' < 0.81 && '+pt_var+' > 400)'
	if 'Tau32Nm1' in iPlot:  cut += ' && ('+soft_massvar+' > 105 && '+soft_massvar+' < 220 && '+pt_var+' > 400)'

	if 'PuppiSDWNm1' in iPlot: cut += ' && ('+puppitau21var+' < 0.55 && '+pt_var+' > 200)'
	if 'PuppiSDRawWNm1' in iPlot: cut += ' && ('+puppitau21var+' < 0.55 && '+pt_var+' > 200)'
	if 'PuppiSDCorrWNm1' in iPlot: cut += ' && ('+puppitau21var+' < 0.55 && '+pt_var+' > 200)'
	if 'PuppiTau21Nm1' in iPlot:  cut += ' && ('+puppi_massvar+' > 65 && '+puppi_massvar+' < 105 && '+pt_var+' > 200)'
	if 'PuppiSDHNm1' in iPlot: cut += ' && ('+nsubsvar+' > 1 && '+pt_var+' > 300)'
	if 'PuppiNsubBNm1' in iPlot: cut += ' && ('+puppi_massvar+' > 60 && '+puppi_massvar+' < 160 && '+pt_var+' > 300)'

	#plot with a specific number of b tags
	if not isCategorized:
		if 'Bjet1' in iPlot or 'Mlb' in iPlot or 'b1' in iPlot: nbtag='1p'
		if 'b2' in iPlot: nbtag='2p'
		if 'Mlj' in iPlot: nbtag='0'

	# Design the tagging cuts for categories
	isEMCut=''
	if isEM=='E': isEMCut+=' && isElectron==1'
	elif isEM=='M': isEMCut+=' && isMuon==1'

	nHtagLJMETname = 'NJetsH1btagged' #shifts will be: nHtagLJMETname+'_shifts[0 -- 7]'
	nWtagLJMETname = 'NJetsWtagged_0p6' #shifts will be: nWtagLJMETname+'_shifts[0/1/2/3/4/5]'
	nbtagLJMETname = 'NJetsCSVwithSF_JetSubCalc' #shifts will be: nbtagLJMETname+'_shifts[0/1/2/3]'
	njetsLJMETname = 'NJets_JetSubCalc' #shifts will be JER/JEC files
	nHtagCut = ''
	nWtagCut = ''
	nbtagCut = ''
	njetsCut = ''
	if isCategorized:
		if nHtag=='0': nHtagCut+= ' && '+nHtagLJMETname+'==0 && '+nHtagLJMETname.replace('H1b','H2b')+'==0'
		elif nHtag=='1b': nHtagCut+=' && '+nHtagLJMETname+'> 0 && '+nHtagLJMETname.replace('H1b','H2b')+'==0'
		elif nHtag=='2b': nHtagCut+=' && '+nHtagLJMETname.replace('H1b','H2b')+'> 0'
		elif nHtag=='1p': nHtagCut+=' && ('+nHtagLJMETname+'> 0 || '+nHtagLJMETname.replace('H1b','H2b')+'> 0)'
		elif nHtag=='0p': nHtagCut=''
	
		if '0p' in nWtag: nWtagCut += ' && ((('+nWtagLJMETname+' > 0 || '+nHtagLJMETname+' > 0 || NJetsH2btagged > 0) && NJets_JetSubCalc >= '+str(cutList['njetsCut'])+') || (('+nWtagLJMETname+' == 0 && '+nHtagLJMETname+' == 0 && NJetsH2btagged == 0) && NJets_JetSubCalc >= '+str(cutList['njetsCut']+1)+'))'
		elif 'p' in nWtag: nWtagCut+=' && '+nWtagLJMETname+'>='+nWtag[:-1]
		else: nWtagCut+=' && '+nWtagLJMETname+'=='+nWtag +' && NJets_JetSubCalc >=' +str(cutList['njetsCut']+1)
		
		if 'p' in nbtag:   # any count in an H tag category should be 'notH' 
			if 'b' in nHtag: nbtagCut += ' && NJetsCSVnotH_JetSubCalc >= '+nbtag[:-1]
			else: nbtagCut+=' && '+nbtagLJMETname+'>='+nbtag[:-1]
		else: 
			if 'b' in nHtag or '1p' in nHtag: nbtagCut += ' && NJetsCSVnotH_JetSubCalc == '+nbtag
			else: nbtagCut+=' && '+nbtagLJMETname+'=='+nbtag
		
		if nbtag=='0' and 'minMlb' in iPlot: 
			origname = plotTreeName
			plotTreeName='minMleppJet'
			if origname != plotTreeName: print 'NEW LJMET NAME:',plotTreeName

		#if ('b' in nHtag or '1p' in nHtag) and iPlot=='minMlbST':
		if ('b' in nHtag or '1p' in nHtag) and (iPlot=='minMlbST' or iPlot=='NXConeJetsST' or iPlot=='minMlbNXConeJetsST' or iPlot=='maxMlep3XConeJetsST'): #added by rizki
			origname = plotTreeName
			plotTreeName = 'AK4HTpMETpLepPt'
			xbins=array('d', linspace(0, 5000, 101).tolist())
			xAxisLabel=';S_{T} (GeV);'	
			if origname != plotTreeName: 
				print 'NEW LJMET NAME:', plotTreeName
				print "x-axis label is set to:", xAxisLabel
				print "using the binning as:", linspace(0, 5000, 101).tolist()

		if ('3p' in nbtag ) and (iPlot=='minMlbNXConeJetsST' or iPlot=='minMlbNXConeJets'): #added by rizki
			origname = plotTreeName
			plotTreeName = 'NXConeJets'
			xbins=array('d', linspace(0, 15, 16).tolist())
			xAxisLabel=';XCone jet multiplicity;'	
			if origname != plotTreeName: 
				print 'NEW LJMET NAME:', plotTreeName
				print "x-axis label is set to:", xAxisLabel
				print "using the binning as:", linspace(0, 15, 16).tolist()

		if ('b' in nHtag or '1p' in nHtag) and (iPlot=='minMlbNXConeJets' or iPlot=='minMlbNXConeJetsV2'): #added by rizki
			origname = plotTreeName
			plotTreeName = 'NXConeJets'
			xbins=array('d', linspace(0, 15, 16).tolist())
			xAxisLabel=';XCone jet multiplicity;'	
			if origname != plotTreeName: 
				print 'NEW LJMET NAME:', plotTreeName
				print "x-axis label is set to:", xAxisLabel
				print "using the binning as:", linspace(0, 15, 16).tolist()

		if ('X4m' in njets) and (iPlot=='STminMlb'): #added by rizki
			origname = plotTreeName
			plotTreeName = 'minMleppBjet'
			xbins=array('d', linspace(0, 1000, 101).tolist())
			xAxisLabel=';min[M(l,b)] (GeV);'	
			if origname != plotTreeName: 
				print 'NEW LJMET NAME:', plotTreeName
				print "x-axis label is set to:", xAxisLabel
				print "using the binning as:", linspace(0, 1000, 101).tolist()

		#if 'p' in njets: njetsCut+=' && '+njetsLJMETname+'>='+njets[:-1]
		#else: njetsCut+=' && '+njetsLJMETname+'=='+njets
		if njets=='0p': njetsCut=''
		if 'p' in njets and 'X' not in njets: njetsCut+=' && '+njetsLJMETname+'>='+njets[:-1] # added by rizki
		elif 'X' not in njets: njetsCut+=' && '+njetsLJMETname+'=='+njets[:-1] # added by rizki
		if 'X' in njets: # added by rizki
			n_ak4jets = njets.split('X')[0] # added by rizki
			if 'p' in n_ak4jets: njetsCut+=' && '+njetsLJMETname+'>='+n_ak4jets[0] # added by rizki
			else: njetsCut+=' && '+njetsLJMETname+'=='+n_ak4jets[0] # added by rizki

			n_xconejets = njets.split('X')[1] # added by rizki
			if 'p' in n_xconejets:  njetsCut+=' && NXConeJets>='+n_xconejets[0] # added by rizki
			if 'm' in n_xconejets:  njetsCut+=' && NXConeJets<='+n_xconejets[0] # added by rizki
 			print 'njets:',njets, 'ak4:',n_ak4jets, 'xcone:',n_xconejets # added by rizki

	else:
		if 'SR' in region: cut += ' && ((('+nWtagLJMETname+' > 0 || '+nHtagLJMETname+' > 0 || NJetsH2btagged > 0) && NJets_JetSubCalc >= '+str(cutList['njetsCut'])+') || (('+nWtagLJMETname+' == 0 && '+nHtagLJMETname+' == 0 && NJetsH2btagged == 0) && NJets_JetSubCalc >= '+str(cutList['njetsCut']+1)+'))'

		if 'p' in nbtag: nbtagCut+=' && '+nbtagLJMETname+'>='+nbtag[:-1]
		else: nbtagCut+=' && '+nbtagLJMETname+'=='+nbtag

		if 'p' in njets: njetsCut+=' && '+njetsLJMETname+'>='+njets[:-1]
		else: njetsCut+=' && '+njetsLJMETname+'=='+njets
		if njets=='0p': njetsCut=''

		
	fullcut = cut+isEMCut+nHtagCut+nWtagCut+nbtagCut+njetsCut

	# replace cuts for shifts
        cut_btagUp = fullcut.replace('btagged','btagged_shifts[0]').replace(nbtagLJMETname,nbtagLJMETname+'_shifts[0]').replace('notH_JetSubCalc','notH_JetSubCalc_shifts[0]')
        cut_btagDn = fullcut.replace('btagged','btagged_shifts[1]').replace(nbtagLJMETname,nbtagLJMETname+'_shifts[1]').replace('notH_JetSubCalc','notH_JetSubCalc_shifts[1]')
        cut_mistagUp = fullcut.replace('btagged','btagged_shifts[2]').replace(nbtagLJMETname,nbtagLJMETname+'_shifts[2]').replace('notH_JetSubCalc','notH_JetSubCalc_shifts[2]')
        cut_mistagDn = fullcut.replace('btagged','btagged_shifts[3]').replace(nbtagLJMETname,nbtagLJMETname+'_shifts[3]').replace('notH_JetSubCalc','notH_JetSubCalc_shifts[3]')
	
	cut_tauUp = fullcut.replace(nWtagLJMETname,nWtagLJMETname+'_shifts[0]')
	cut_tauDn = fullcut.replace(nWtagLJMETname,nWtagLJMETname+'_shifts[1]')
	cut_tauptUp = fullcut.replace(nWtagLJMETname,nWtagLJMETname+'_shifts[6]')
	cut_tauptDn = fullcut.replace(nWtagLJMETname,nWtagLJMETname+'_shifts[7]')
	cut_jmsUp = fullcut.replace(nWtagLJMETname,nWtagLJMETname+'_shifts[2]').replace('btagged','btagged_shifts[4]').replace('notH_JetSubCalc','notH_JetSubCalc_shifts[4]')
	cut_jmsDn = fullcut.replace(nWtagLJMETname,nWtagLJMETname+'_shifts[3]').replace('btagged','btagged_shifts[5]').replace('notH_JetSubCalc','notH_JetSubCalc_shifts[5]')
	cut_jmrUp = fullcut.replace(nWtagLJMETname,nWtagLJMETname+'_shifts[4]').replace('btagged','btagged_shifts[6]').replace('notH_JetSubCalc','notH_JetSubCalc_shifts[6]')
	cut_jmrDn = fullcut.replace(nWtagLJMETname,nWtagLJMETname+'_shifts[5]').replace('btagged','btagged_shifts[7]').replace('notH_JetSubCalc','notH_JetSubCalc_shifts[7]')
	
	# cut_topsfUp = fullcut.replace(nttagLJMETname,nttagLJMETname+'_shifts[0]')
	# cut_topsfDn = fullcut.replace(nttagLJMETname,nttagLJMETname+'_shifts[1]')

	print 'plotTreeName: '+plotTreeName
	print 'Flavour: '+isEM+' #Htags: '+nHtag+' #Wtags: '+nWtag+' #btags: '+nbtag+' #jets: '+njets
	print "Weights:",weightStr
	print 'Cuts: '+fullcut

	# Declare histograms
	hists = {}
	hists[iPlot+'_'+lumiStr+'fb_'+catStr+'_'+process]  = TH1D(iPlot+'_'+lumiStr+'fb_'+catStr+'_'+process,xAxisLabel,len(xbins)-1,xbins)
	if doAllSys:
		hists[iPlot+'trigeffUp_'    +lumiStr+'fb_'+catStr+'_'+process] = TH1D(iPlot+'trigeffUp_'    +lumiStr+'fb_'+catStr+'_'+process,xAxisLabel,len(xbins)-1,xbins)
		hists[iPlot+'trigeffDown_'  +lumiStr+'fb_'+catStr+'_'+process] = TH1D(iPlot+'trigeffDown_'  +lumiStr+'fb_'+catStr+'_'+process,xAxisLabel,len(xbins)-1,xbins)
		hists[iPlot+'pileupUp_'     +lumiStr+'fb_'+catStr+'_'+process] = TH1D(iPlot+'pileupUp_'     +lumiStr+'fb_'+catStr+'_'+process,xAxisLabel,len(xbins)-1,xbins)
		hists[iPlot+'pileupDown_'   +lumiStr+'fb_'+catStr+'_'+process] = TH1D(iPlot+'pileupDown_'   +lumiStr+'fb_'+catStr+'_'+process,xAxisLabel,len(xbins)-1,xbins)
		hists[iPlot+'muRFcorrdUp_'  +lumiStr+'fb_'+catStr+'_'+process] = TH1D(iPlot+'muRFcorrdUp_'  +lumiStr+'fb_'+catStr+'_'+process,xAxisLabel,len(xbins)-1,xbins)
		hists[iPlot+'muRFcorrdDown_'+lumiStr+'fb_'+catStr+'_'+process] = TH1D(iPlot+'muRFcorrdDown_'+lumiStr+'fb_'+catStr+'_'+process,xAxisLabel,len(xbins)-1,xbins)
		hists[iPlot+'muRUp_'        +lumiStr+'fb_'+catStr+'_'+process] = TH1D(iPlot+'muRUp_'        +lumiStr+'fb_'+catStr+'_'+process,xAxisLabel,len(xbins)-1,xbins)
		hists[iPlot+'muRDown_'      +lumiStr+'fb_'+catStr+'_'+process] = TH1D(iPlot+'muRDown_'      +lumiStr+'fb_'+catStr+'_'+process,xAxisLabel,len(xbins)-1,xbins)
		hists[iPlot+'muFUp_'        +lumiStr+'fb_'+catStr+'_'+process] = TH1D(iPlot+'muFUp_'        +lumiStr+'fb_'+catStr+'_'+process,xAxisLabel,len(xbins)-1,xbins)
		hists[iPlot+'muFDown_'      +lumiStr+'fb_'+catStr+'_'+process] = TH1D(iPlot+'muFDown_'      +lumiStr+'fb_'+catStr+'_'+process,xAxisLabel,len(xbins)-1,xbins)
		hists[iPlot+'topptUp_'      +lumiStr+'fb_'+catStr+'_'+process] = TH1D(iPlot+'topptUp_'      +lumiStr+'fb_'+catStr+'_'+process,xAxisLabel,len(xbins)-1,xbins)
		hists[iPlot+'topptDown_'    +lumiStr+'fb_'+catStr+'_'+process] = TH1D(iPlot+'topptDown_'    +lumiStr+'fb_'+catStr+'_'+process,xAxisLabel,len(xbins)-1,xbins)
		hists[iPlot+'tauptUp_'      +lumiStr+'fb_'+catStr+'_'+process] = TH1D(iPlot+'tauptUp_'      +lumiStr+'fb_'+catStr+'_'+process,xAxisLabel,len(xbins)-1,xbins)
		hists[iPlot+'tauptDown_'    +lumiStr+'fb_'+catStr+'_'+process] = TH1D(iPlot+'tauptDown_'    +lumiStr+'fb_'+catStr+'_'+process,xAxisLabel,len(xbins)-1,xbins)
		hists[iPlot+'btagUp_'       +lumiStr+'fb_'+catStr+'_'+process] = TH1D(iPlot+'btagUp_'       +lumiStr+'fb_'+catStr+'_'+process,xAxisLabel,len(xbins)-1,xbins)
		hists[iPlot+'btagDown_'     +lumiStr+'fb_'+catStr+'_'+process] = TH1D(iPlot+'btagDown_'     +lumiStr+'fb_'+catStr+'_'+process,xAxisLabel,len(xbins)-1,xbins)
		hists[iPlot+'mistagUp_'     +lumiStr+'fb_'+catStr+'_'+process] = TH1D(iPlot+'mistagUp_'     +lumiStr+'fb_'+catStr+'_'+process,xAxisLabel,len(xbins)-1,xbins)
		hists[iPlot+'mistagDown_'   +lumiStr+'fb_'+catStr+'_'+process] = TH1D(iPlot+'mistagDown_'   +lumiStr+'fb_'+catStr+'_'+process,xAxisLabel,len(xbins)-1,xbins)
		hists[iPlot+'tau21Up_'      +lumiStr+'fb_'+catStr+'_'+process] = TH1D(iPlot+'tau21Up_'      +lumiStr+'fb_'+catStr+'_'+process,xAxisLabel,len(xbins)-1,xbins)
		hists[iPlot+'tau21Down_'    +lumiStr+'fb_'+catStr+'_'+process] = TH1D(iPlot+'tau21Down_'    +lumiStr+'fb_'+catStr+'_'+process,xAxisLabel,len(xbins)-1,xbins)
		hists[iPlot+'jmsUp_'        +lumiStr+'fb_'+catStr+'_'+process] = TH1D(iPlot+'jmsUp_'      +lumiStr+'fb_'+catStr+'_'+process,xAxisLabel,len(xbins)-1,xbins)
		hists[iPlot+'jmsDown_'      +lumiStr+'fb_'+catStr+'_'+process] = TH1D(iPlot+'jmsDown_'    +lumiStr+'fb_'+catStr+'_'+process,xAxisLabel,len(xbins)-1,xbins)
		hists[iPlot+'jmrUp_'        +lumiStr+'fb_'+catStr+'_'+process] = TH1D(iPlot+'jmrUp_'      +lumiStr+'fb_'+catStr+'_'+process,xAxisLabel,len(xbins)-1,xbins)
		hists[iPlot+'jmrDown_'      +lumiStr+'fb_'+catStr+'_'+process] = TH1D(iPlot+'jmrDown_'    +lumiStr+'fb_'+catStr+'_'+process,xAxisLabel,len(xbins)-1,xbins)
		hists[iPlot+'jsfUp_'        +lumiStr+'fb_'+catStr+'_'+process] = TH1D(iPlot+'jsfUp_'        +lumiStr+'fb_'+catStr+'_'+process,xAxisLabel,len(xbins)-1,xbins)
		hists[iPlot+'jsfDown_'      +lumiStr+'fb_'+catStr+'_'+process] = TH1D(iPlot+'jsfDown_'      +lumiStr+'fb_'+catStr+'_'+process,xAxisLabel,len(xbins)-1,xbins)
		# hists[iPlot+'topsfUp_'      +lumiStr+'fb_'+catStr+'_'+process] = TH1D(iPlot+'topsfUp_'      +lumiStr+'fb_'+catStr+'_'+process,xAxisLabel,len(xbins)-1,xbins)
		# hists[iPlot+'topsfDown_'    +lumiStr+'fb_'+catStr+'_'+process] = TH1D(iPlot+'topsfDown_'    +lumiStr+'fb_'+catStr+'_'+process,xAxisLabel,len(xbins)-1,xbins)
			
# 		if tTree[process+'jerUp']: 
# 			hists[iPlot+'jerUp_'   +lumiStr+'fb_'+catStr+'_'+process]  = TH1D(iPlot+'jerUp_'   +lumiStr+'fb_'+catStr+'_'+process,xAxisLabel,len(xbins)-1,xbins)
# 			hists[iPlot+'jerDown_' +lumiStr+'fb_'+catStr+'_'+process]  = TH1D(iPlot+'jerDown_' +lumiStr+'fb_'+catStr+'_'+process,xAxisLabel,len(xbins)-1,xbins)
# 		if tTree[process+'jecUp']:
# 			hists[iPlot+'jecUp_'   +lumiStr+'fb_'+catStr+'_'+process]  = TH1D(iPlot+'jecUp_'   +lumiStr+'fb_'+catStr+'_'+process,xAxisLabel,len(xbins)-1,xbins)
# 			hists[iPlot+'jecDown_' +lumiStr+'fb_'+catStr+'_'+process]  = TH1D(iPlot+'jecDown_' +lumiStr+'fb_'+catStr+'_'+process,xAxisLabel,len(xbins)-1,xbins)
		for i in range(100): hists[iPlot+'pdf'+str(i)+'_'+lumiStr+'fb_'+catStr+'_'+process] = TH1D(iPlot+'pdf'+str(i)+'_'+lumiStr+'fb_'+catStr+'_'+process,xAxisLabel,len(xbins)-1,xbins)
	for key in hists.keys(): hists[key].Sumw2()

	# DRAW histograms
# 	print 'plotTreeName = ',plotTreeName
# 	print 'iPlot = ',iPlot
# 	print 'lumiStr = ',lumiStr
# 	print 'catStr = ',catStr
# 	print 'process = ',process
# 	print 'weightStr = ',weightStr
# 	print 'fullcut = ',fullcut
# 	tTree[process].Print()
# 	print ''
	tTree[process].Draw(plotTreeName+' >> '+iPlot+''+'_'+lumiStr+'fb_'+catStr+'_' +process, weightStr+'*('+fullcut+')', 'GOFF')
	if doAllSys:
		tTree[process].Draw(plotTreeName+' >> '+iPlot+'trigeffUp_'    +lumiStr+'fb_'+catStr+'_'+process, weightTrigEffUpStr+'*('+fullcut+')', 'GOFF')
		tTree[process].Draw(plotTreeName+' >> '+iPlot+'trigeffDown_'  +lumiStr+'fb_'+catStr+'_'+process, weightTrigEffDownStr+'*('+fullcut+')', 'GOFF')
		tTree[process].Draw(plotTreeName+' >> '+iPlot+'pileupUp_'     +lumiStr+'fb_'+catStr+'_'+process, weightPileupUpStr+'*('+fullcut+')', 'GOFF')
		tTree[process].Draw(plotTreeName+' >> '+iPlot+'pileupDown_'   +lumiStr+'fb_'+catStr+'_'+process, weightPileupDownStr+'*('+fullcut+')', 'GOFF')
		tTree[process].Draw(plotTreeName+' >> '+iPlot+'muRFcorrdUp_'  +lumiStr+'fb_'+catStr+'_'+process, weightmuRFcorrdUpStr  +'*('+fullcut+')', 'GOFF')
		tTree[process].Draw(plotTreeName+' >> '+iPlot+'muRFcorrdDown_'+lumiStr+'fb_'+catStr+'_'+process, weightmuRFcorrdDownStr+'*('+fullcut+')', 'GOFF')
		tTree[process].Draw(plotTreeName+' >> '+iPlot+'muRUp_'        +lumiStr+'fb_'+catStr+'_'+process, weightmuRUpStr+'*('+fullcut+')', 'GOFF')
		tTree[process].Draw(plotTreeName+' >> '+iPlot+'muRDown_'      +lumiStr+'fb_'+catStr+'_'+process, weightmuRDownStr+'*('+fullcut+')', 'GOFF')
		tTree[process].Draw(plotTreeName+' >> '+iPlot+'muFUp_'        +lumiStr+'fb_'+catStr+'_'+process, weightmuFUpStr+'*('+fullcut+')', 'GOFF')
		tTree[process].Draw(plotTreeName+' >> '+iPlot+'muFDown_'      +lumiStr+'fb_'+catStr+'_'+process, weightmuFDownStr+'*('+fullcut+')', 'GOFF')
		tTree[process].Draw(plotTreeName+' >> '+iPlot+'topptUp_'      +lumiStr+'fb_'+catStr+'_'+process, weighttopptUpStr+'*('+fullcut+')', 'GOFF')
		tTree[process].Draw(plotTreeName+' >> '+iPlot+'topptDown_'    +lumiStr+'fb_'+catStr+'_'+process, weighttopptDownStr+'*('+fullcut+')', 'GOFF')
		tTree[process].Draw(plotTreeName+' >> '+iPlot+'jsfUp_'        +lumiStr+'fb_'+catStr+'_'+process, weightjsfUpStr+'*('+fullcut+')', 'GOFF')
		tTree[process].Draw(plotTreeName+' >> '+iPlot+'jsfDown_'      +lumiStr+'fb_'+catStr+'_'+process, weightjsfDownStr+'*('+fullcut+')', 'GOFF')

		# Change the plot name itself for shifts if needed
		# TTAGupName= plotTreeName
		# TTAGdnName= plotTreeName
		# if 'Ttagged' in TTAGupName or 'Tjet' in TTAGupName or 'TJet' in TTAGupName: 
		# 	TTAGupName = TTAGupName+'_shifts[0]'
		# 	TTAGdnName = TTAGdnName+'_shifts[1]'
		# print 'TTAG SHIFT LJMET NAMES',TTAGupName,TTAGdnName
		# tTree[process].Draw(TTAGupName+' >> '+iPlot+'topsfUp_'  +lumiStr+'fb_'+catStr+'_'+process, weightStr+'*('+cut_topsfUp+')', 'GOFF')
		# tTree[process].Draw(TTAGdnName+' >> '+iPlot+'topsfDown_'+lumiStr+'fb_'+catStr+'_'+process, weightStr+'*('+cut_topsfDn+')', 'GOFF')

		JMRupName = plotTreeName
		JMRdnName = plotTreeName
		JMSupName = plotTreeName
		JMSdnName = plotTreeName
		TAUupName = plotTreeName
		TAUdnName = plotTreeName
		TAUPTupName = plotTreeName
		TAUPTdnName = plotTreeName
		if 'Wtagged' in TAUupName or 'Wjet' in TAUupName or 'WJet' in TAUupName: 
			TAUupName = TAUupName+'_shifts[0]'
			TAUdnName = TAUdnName+'_shifts[1]'			
			JMSupName = JMSupName+'_shifts[2]'
			JMSdnName = JMSdnName+'_shifts[3]'
			JMRupName = JMRupName+'_shifts[4]'
			JMRdnName = JMRdnName+'_shifts[5]'
			TAUPTupName = TAUPTupName+'_shifts[6]'
			TAUPTdnName = TAUPTdnName+'_shifts[7]'			
		elif 'WtagUncerts' in TAUupName:
			JMSupName = JMSupName.replace('Uncerts','Uncerts_JMSup')
			JMSdnName = JMSdnName.replace('Uncerts','Uncerts_JMSdn')
			JMRupName = JMRupName.replace('Uncerts','Uncerts_JMRup')
			JMRdnName = JMRdnName.replace('Uncerts','Uncerts_JMRdn')
		elif 'btagged' in TAUupName or 'notH' in TAUupName or 'notPH' in TAUupName:
			JMSupName = JMSupName+'_shifts[4]'
			JMSdnName = JMSdnName+'_shifts[5]'
			JMRupName = JMRupName+'_shifts[6]'
			JMRdnName = JMRdnName+'_shifts[7]'			
		print 'TAG SHIFT LJMET NAMES',TAUupName,TAUdnName,JMRupName,JMRdnName,JMSupName,JMSdnName,
		tTree[process].Draw(JMRupName+' >> '+iPlot+'jmrUp_'    +lumiStr+'fb_'+catStr+'_'+process, weightStr+'*('+cut_jmrUp+')', 'GOFF')
		tTree[process].Draw(JMRdnName+' >> '+iPlot+'jmrDown_'  +lumiStr+'fb_'+catStr+'_'+process, weightStr+'*('+cut_jmrDn+')', 'GOFF')
		tTree[process].Draw(JMSupName+' >> '+iPlot+'jmsUp_'    +lumiStr+'fb_'+catStr+'_'+process, weightStr+'*('+cut_jmsUp+')', 'GOFF')
		tTree[process].Draw(JMSdnName+' >> '+iPlot+'jmsDown_'  +lumiStr+'fb_'+catStr+'_'+process, weightStr+'*('+cut_jmsDn+')', 'GOFF')
		tTree[process].Draw(TAUupName+' >> '+iPlot+'tau21Up_'  +lumiStr+'fb_'+catStr+'_'+process, weightStr+'*('+cut_tauUp+')', 'GOFF')
		tTree[process].Draw(TAUdnName+' >> '+iPlot+'tau21Down_'+lumiStr+'fb_'+catStr+'_'+process, weightStr+'*('+cut_tauDn+')', 'GOFF')		
		tTree[process].Draw(TAUPTupName+' >> '+iPlot+'tauptUp_'  +lumiStr+'fb_'+catStr+'_'+process, weightStr+'*('+cut_tauptUp+')', 'GOFF')
		tTree[process].Draw(TAUPTdnName+' >> '+iPlot+'tauptDown_'+lumiStr+'fb_'+catStr+'_'+process, weightStr+'*('+cut_tauptDn+')', 'GOFF') 

		BTAGupName = plotTreeName.replace('_lepBJets','_bSFup_lepBJets')
		BTAGdnName = plotTreeName.replace('_lepBJets','_bSFdn_lepBJets')
		MISTAGupName = plotTreeName.replace('_lepBJets','_lSFup_lepBJets')
		MISTAGdnName = plotTreeName.replace('_lepBJets','_lSFdn_lepBJets')
		if 'CSVwithSF' in BTAGupName or 'btagged' in BTAGupName or 'MleppB' in BTAGupName or 'BJetLead' in BTAGupName or 'minMlb' in BTAGupName or 'notH' in BTAGupName or 'notPH' in BTAGupName:
			BTAGupName = BTAGupName+'_shifts[0]'
			BTAGdnName = BTAGdnName+'_shifts[1]'
			MISTAGupName = MISTAGupName+'_shifts[2]'
			MISTAGdnName = MISTAGdnName+'_shifts[3]'
		print 'BTAG SHIFT LJMET NAMES',BTAGupName,BTAGdnName,MISTAGupName,MISTAGdnName
		tTree[process].Draw(BTAGupName+' >> '+iPlot+'btagUp_'  +lumiStr+'fb_'+catStr+'_'+process, weightStr+'*('+cut_btagUp+')', 'GOFF')
		tTree[process].Draw(BTAGdnName+' >> '+iPlot+'btagDown_'+lumiStr+'fb_'+catStr+'_'+process, weightStr+'*('+cut_btagDn+')', 'GOFF')
		tTree[process].Draw(MISTAGupName+' >> '+iPlot+'mistagUp_'  +lumiStr+'fb_'+catStr+'_'+process, weightStr+'*('+cut_mistagUp+')', 'GOFF')
		tTree[process].Draw(MISTAGdnName+' >> '+iPlot+'mistagDown_'+lumiStr+'fb_'+catStr+'_'+process, weightStr+'*('+cut_mistagDn+')', 'GOFF')

# 		if tTree[process+'jecUp']:
# 			tTree[process+'jecUp'].Draw(plotTreeName   +' >> '+iPlot+'jecUp_'  +lumiStr+'fb_'+catStr+'_' +process, weightStr+'*('+fullcut+')', 'GOFF')
# 			tTree[process+'jecDown'].Draw(plotTreeName +' >> '+iPlot+'jecDown_'+lumiStr+'fb_'+catStr+'_' +process, weightStr+'*('+fullcut+')', 'GOFF')
# 		if tTree[process+'jerUp']:
# 			tTree[process+'jerUp'].Draw(plotTreeName   +' >> '+iPlot+'jerUp_'  +lumiStr+'fb_'+catStr+'_' +process, weightStr+'*('+fullcut+')', 'GOFF')
# 			tTree[process+'jerDown'].Draw(plotTreeName +' >> '+iPlot+'jerDown_'+lumiStr+'fb_'+catStr+'_' +process, weightStr+'*('+fullcut+')', 'GOFF')
		for i in range(100): tTree[process].Draw(plotTreeName+' >> '+iPlot+'pdf'+str(i)+'_'+lumiStr+'fb_'+catStr+'_'+process, 'pdfWeights['+str(i)+'] * '+weightStr+'*('+fullcut+')', 'GOFF')
	
	for key in hists.keys(): hists[key].SetDirectory(0)	
	return hists
