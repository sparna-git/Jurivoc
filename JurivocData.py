import os
import pandas as pd

blockS_ID = ["UF","BT","SN","SA","USE","UFA","NT","USA","AND"]
LANGUAGE_DICT = {"ITA":"it","GER":"de"}
langID = ['GER','ITA']

class dataset:

    def __init__(self, directory_input):
        # directory input files
        self.directoryFile = directory_input
        # Save all Name of file and dataframe
        self.recordOutput = []

    def readFiles(self) -> list:

        dataset = []
        source_language = []
        for f in os.listdir(self.directoryFile):
            nameFile = f
            filename = os.path.splitext(os.path.basename(f))[0]
            fileInput = os.path.join(self.directoryFile, f)
            if os.path.isfile(fileInput):
                f = open(fileInput,'r', encoding="ISO-8859-1")
                rows = f.readlines()
                
                dfGetStructure = pd.DataFrame(
                    (
                        # read the data and save in the dataframe
                        [len(row)-len(row.lstrip()), row.replace("\n", "")] for row in rows
                    ), 
                    columns = ("level","title")
                )

                # Remove all rows not necessary
                dfGetStructure.drop(dfGetStructure[dfGetStructure["level"] == 0].index, inplace=True)
                dfGetStructure['title'] = dfGetStructure['title'].str.lstrip()
                # remove all row when title row is empty
                dfGetStructure.drop(dfGetStructure[dfGetStructure["title"] == ''].index, inplace=True)
                df = dfGetStructure.reset_index(drop=True)

                print("File: {}".format(filename))
                if "_fre_" in filename:
                    # Update df for language
                    dfGetStructure.to_csv('language.csv',sep="|",index=False)
                    source_language.append(self.language_processing(df, filename))
                else:
                    # Preprocessing 
                    dftitles = self.update_titles(df)
                    # Add block Column
                    dfblock = self.add_block_column(dftitles)
                    # Add title_block Column
                    dftitle_block = self.add_title_block(dfblock)
                    # Preporcessing all 
                    dfUpdateblock = self.update_title_block(dftitle_block)
                    
                    dfUpdateBT = self.update_title_block_joint(dfUpdateblock,'BT')
                    dfUpdateUF = self.update_title_block_joint(dfUpdateBT,'UF')
                    dfUpdateUSA = self.update_title_block_joint(dfUpdateUF,'USA')
                    dfUpdateAND = self.update_title_block_joint(dfUpdateUSA,'AND')
                    dfUpdateSA = self.update_title_block_joint(dfUpdateAND,'SA')
                    dfOutput = self.update_sn_block(dfUpdateSA)

                    #dfOutput.to_csv('Temp1.csv',sep="|",index=False)
                    dataset.append([filename,dfOutput])

        # Preprocessing for language DF
        if len(source_language) > 0:            
            dataset.append(["dbLanguage",pd.concat(source_language)])
        return dataset

    def update_titles(self, df:pd.DataFrame) -> pd.DataFrame:

        print("Update title ...")
        # Evaluate and update dataframe
        indexMax = pd.Series(df['level'].squeeze()).index.max()
        data_duplicate = []
        data = []
        auxtitle = ''
        auxtitle_full = ''
        level_nextValue = 0
        for idx, row in df.iterrows():
            
            # Update title header
            if idx < indexMax:
                nextIdx = idx+1
                level_nextValue = df.at[idx+1,"level"]            
                
            if int(row['level']) == 1:
                if row['level'] == level_nextValue:
                    # Update title
                    title = row['title'] + ' ' + df.at[nextIdx,'title']
                    #data_duplicate.append([df.at[idx+1,"title"],title])
                    data.append([row['level'],title])
                    auxtitle = df.at[nextIdx,'title']
                    auxtitle_full = title                    
                else:
                    if row['title'] != auxtitle:
                        data.append([row['level'],row['title']])
                #    else:
                #        data.append([row['level'],auxtitle_full])
            else:
                    if row['title'] != auxtitle:
                        data.append([row['level'],row['title']])
                    else:
                        data.append([row['level'],auxtitle_full])
            
        dfProcess = pd.DataFrame(data=data,columns=['level','title'])        
        return dfProcess
    
    def get_block(self,level,title) -> str:

        Bock_Key = ""
        if int(level ) > 1:
            try:
                idblock = title.split()[0].lstrip()
                nItem = len(title.split())
                
                if nItem > 1:
                    if idblock in blockS_ID:
                        Bock_Key = idblock
                    elif idblock in langID:
                        Bock_Key = idblock
                    else:
                        Bock_Key = ''
                else:
                    Bock_Key = ''
            except:
                Bock_Key = ''
        return Bock_Key
    
    def add_block_column(self,df:pd.DataFrame) -> pd.DataFrame:

        print("Add block ...")
        # Add block
        df["block"] = df.apply(lambda t : self.get_block(t['level'],t['title']), axis=1)
        return df

    def split_title(self,level:str,block:str,title:str) -> str:
        titleblock = ''
        if int(level) > 1:
            if bool(block):
                try:
                    listtitle = title.split()
                    listtitle.remove(block)
                    titleblock = " ".join(listtitle).lstrip()
                except:
                    titleblock = title                    
            else:
                titleblock = title
        return titleblock

    def add_title_block(self,df:pd.DataFrame) -> pd.DataFrame:

        print("Add Title Block ...")
        df["title_block"] = df.apply(lambda t : self.split_title(t['level'],t['block'],t['title']), axis=1)
        return df
    
    def update_title_block(self,df:pd.DataFrame) -> pd.DataFrame:
        
        print("Update Title Block ...")
        data = []
        blockAux = ''
        titleAux = ''
        for idx,row in df.iterrows():            
            nlevel = int(row['level'])
            block = row['block']

            if nlevel == 1:
                titleAux = row['title']
                data.append([row['level'],row['title'],row['block'],row['title_block']])
            else:
                if block:
                    # Get block Id
                    blockAux = block
                    data.append([row['level'],titleAux,block,row['title_block']])                 
                else:
                    data.append([row['level'],titleAux,blockAux,row['title_block']])                

        dfUpdate = pd.DataFrame(data = data,columns=['level','title','block','title_block'])
        return dfUpdate

    def update_title_block_joint(self,df:pd.DataFrame,blockId :str) -> pd.DataFrame:
        # Evaluate and update dataframe
        indexMax = pd.Series(df['level'].squeeze()).index.max()
        data_duplicate = []
        data = []
        auxtitle = ''
        nextIdx = 0
        for idx, row in df.iterrows():

            level = row['level']
            titleH = row['title']
            block = row['block']
            titleBlock = row['title_block']

            # Update title header
            if idx < indexMax:
                nextIdx = idx+1

            sTitleBlock = ""
            if block == blockId:
                if titleBlock == auxtitle:
                    data_duplicate.append([titleH,titleBlock])
                else:
                    # find text how title header
                    dfTmp = df[df['title'].isin([titleBlock])]
                    if len(dfTmp) > 0:
                        sTitleBlock = titleBlock                     
                    else:
                        # Update title
                        title_joint = titleBlock + ' ' + df.iloc[nextIdx].at['title_block']
                        #print('title {} | block {} | title {}'.format(titleH,block,title_joint))
                        dfTmp2 = df[df['title'].isin([title_joint])]
                        if len(dfTmp2) > 0:
                            auxtitle = df.iloc[nextIdx].at['title_block']
                            sTitleBlock = title_joint
                        else:
                            sTitleBlock = titleBlock
                if len(sTitleBlock) > 0:
                    data.append([level,titleH,block,sTitleBlock])
            else:
                data.append([level,titleH,block,titleBlock])
        
        dfOtput = pd.DataFrame(data=data,columns=['level','title','block','title_block'])
        
        return dfOtput
    
    def update_sn_block(self,df:pd.DataFrame) -> pd.DataFrame:
        print('Update dataframe SN...')

        titlesKey = pd.Series(df['title'].to_list()).drop_duplicates().to_list()
        data = []
        datalist = []
        for title in titlesKey:
            # Get Dataframe block from title id
            dfFilter = df[df['title'].isin([title])]
            blocks = pd.Series(dfFilter['block'].to_list()).drop_duplicates().to_list()
            if 'SN' in blocks:
                #Filter SN in Dataframe 
                dfFilterSN = dfFilter[dfFilter['block'].isin(["SN"])]
                if len(dfFilterSN) > 1:
                    # Get all SN title
                    str_note = " ".join(str(x) for x in dfFilterSN["title_block"].to_list())
                    # Drop all SN row 
                    dftemp = dfFilter.drop(dfFilter[dfFilter["block"] == "SN"].index)
                    for l in dftemp.values.tolist():  
                        datalist.append(l)
                    # Add row SN in dataframe
                    datalist.append(["3",title,"SN",str_note])                    
                else:
                    for l in dfFilter.values.tolist():
                        datalist.append(l)
            else:
                for l in dfFilter.values.tolist():
                    datalist.append(l)
        
        dfTmp = pd.DataFrame(data = datalist, columns=["level","title","block","title_block"])
        return dfTmp

    def language_processing(self, df:pd.DataFrame, nameFile: str) -> pd.DataFrame:

        dftitles = self.update_titles(df)
        
        df_block = self.add_block_column(dftitles)
        df_title = self.add_title_block(df_block)

        dfUpdateBT = self.update_title_block_joint(df_title,'BT')
        dfUpdateUF = self.update_title_block_joint(dfUpdateBT,'UF')
        dfUpdateUSA = self.update_title_block_joint(dfUpdateUF,'USA')
        dfUpdateAND = self.update_title_block_joint(dfUpdateUSA,'AND')
        dfUpdateSA = self.update_title_block_joint(dfUpdateAND,'SA')
        dfLanguage = self.update_title_block(dfUpdateSA)

        dftmp = dfLanguage[dfLanguage['level'] > 1]
        dfTmp2 = dftmp.reset_index(drop=True)
        dfOutputLanguage = dfTmp2.drop(['level'], axis=1)
        dfOutput = dfOutputLanguage.rename(columns={"block":"language","title_block":"title_traduction"})
        
        dfOutput['language'] = dfOutput['language'].apply([lambda l : LANGUAGE_DICT[l]])

        return dfOutput

    def read_file(self) -> list:
        # Return a list with name of file and dataframe
        return self.readFiles()