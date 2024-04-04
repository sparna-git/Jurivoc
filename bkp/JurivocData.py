import os
import pandas as pd
import logging as log

LANGUAGES = ["ITA","GER"]
LANGUAGE_DICT = {"ITA":"it","GER":"de"}
BLOCKS_ID = ["UF","BT","SN","SA","USE","UFA","NT","USA","AND"]

class dataset:

    def __init__(self, directory_input):
        # directory input files
        self.directoryFile = directory_input
        # Save all Name of file and dataframe
        self.recordOutput = []

    def readFileInput(self) -> list:

        source_language = []
        for f in os.listdir(self.directoryFile):
            nameFile = f
            fileInput = os.path.join(self.directoryFile, f)
            if os.path.isfile(fileInput):
                print("File: " + fileInput)
                f = open(fileInput,'r', encoding="ISO-8859-1")
                rows = f.readlines()
                
                dfGetStructure = pd.DataFrame(
                    (
                        # read the data and save in the dataframe
                        [len(row)-len(row.lstrip()), row.replace("\n", "")] for row in rows
                    ), 
                    columns = ("Level","Title")
                )        
            
            # Data Quality process
            dfPreprocessing = self.preprocessing(dfGetStructure)
            if "_fre_" in nameFile:
                # Update df for language
                source_language.append(self.language_processing(dfPreprocessing, nameFile))
            else:
                self.recordOutput.append([nameFile,dfPreprocessing])

        # Preprocessing for language DF
        if len(source_language) > 0:            
            self.recordOutput.append(["dbLanguage",pd.concat(source_language)])                
        
        return self.recordOutput
    
    def preprocessing(self, df) -> pd.DataFrame:
        
        # Delete all row what your content is 1 or 1(cont)
        df.drop(df[df["Level"] == 0].index, inplace=True)
        # Create dataframe temp and update
        Dataset= self.split_row_data(df)
        dfTmp = pd.DataFrame(data=Dataset,columns=['Level', 'title','block','title_block'])
        dfUpdate = self.update_title(dfTmp)
        dfBlock = self.update_block(dfUpdate)
        dfOutput = self.processing_block_sn(dfBlock)
        return dfOutput

    def split_row_data(self,df:pd.DataFrame) -> list:

        data = []
        # Get id Start Level
        nLevel = df["Level"].astype("Int64").min()
        titleHeaderAux = ""        
        titleHeader = ""
        for index, row in df.iterrows():
            idLevel = row["Level"]
            titleLevel = row["Title"]

            block = ""
            title = ""            
            title_ = ""

            if titleLevel.isspace() == False:
                title_dataquality =" ".join(titleLevel.split())
                try:
                    idBlock = title_dataquality.split()[0]
                    if idBlock in BLOCKS_ID:
                        block = idBlock
                        # Valider
                        lTitle = title_dataquality.split()
                        lTitle.remove(block)
                        title = " ".join(lTitle).lstrip()
                except:
                    block = ""
                            
                if len(title) == 0:
                    title = title_dataquality
                
                if idLevel == 1:
                    titleHeader = title
                    titleHeaderAux = titleHeader
                else:
                    titleHeader = titleHeaderAux
                    title_ = title
                #print("{}|{}|{}|{}".format(idLevel,titleHeader,block,title_))
                data.append([idLevel,titleHeader,block,title_])
        
        return data

    def find_list_title(self,titlelist : list,titleValue:str) -> str:

        t = ""
        for title in titlelist:
            if title[0] == titleValue:
                t = title[1]
                break

        if len(t)> 0:
            return t
        else:
            return titleValue

        return True    
    
    def update_title(self,df:pd.DataFrame) -> pd.DataFrame:
        
        # Evaluate and update dataframe
        indexMax = pd.Series(df["Level"].squeeze()).index.max()
        data = []
        data_duplicate = []
        auxtitle = ""
        auxtitle_full = ""
        for index, row in df.iterrows():
            idLevel = str(row["Level"])
            titleH = str(row["title"])
            
            idBlock = str(row["block"])
            titleBlock = str(row["title_block"])

            # Update title header
            if index < indexMax:
                Level_nextValue = df.at[index+1,"Level"]
            
            if row["Level"] == 1:
                if row["Level"] == Level_nextValue:
                    # Update title
                    title = df.at[index,'title'] + ' ' + df.at[index+1,"title"]
                    data_duplicate.append([df.at[index+1,"title"],title])
                    data.append([idLevel,title,idBlock, titleBlock])
                    auxtitle = df.at[index+1,"title"]
                    auxtitle_full = title
                else:
                    if titleH != auxtitle:
                        data.append([idLevel,titleH,idBlock, titleBlock])
                    else:
                        data.append([idLevel,auxtitle_full,idBlock, titleBlock])
            else:
                if titleH != auxtitle:
                    data.append([idLevel,titleH,idBlock, titleBlock])
                else:
                    data.append([idLevel,auxtitle_full,idBlock, titleBlock])
        lists_data = pd.Series(data).drop_duplicates().to_list()
        dfTemp = pd.DataFrame(data = lists_data,columns=["Level","title","block","title_block"])
        
        return dfTemp 

    def update_block(self,df:pd.DataFrame) -> pd.DataFrame:

        blockAux = ""
        for index,row in df.iterrows():
            nLevel = row["Level"]
            block =  row["block"]
            if int(nLevel) > 1:
                if block:
                    # Get block Id
                    blockAux = block                   
                else:
                    row["block"] = blockAux            
        return df

    def processing_block_sn(self,df:pd.DataFrame) -> pd.DataFrame:
        
        titlesKey = pd.Series(df["title"].to_list()).drop_duplicates().to_list()
        data = []
        datalist = []
        for title in titlesKey:
            # Get Dataframe block from title id
            dfFilter = df[df["title"].isin([title])]
            blocks = pd.Series(dfFilter["block"].to_list()).drop_duplicates().to_list() #list(dict.fromkeys(dfFilter["block"].to_list()))
            if 'SN' in blocks:
                #Filter SN in Dataframe 
                dfFilterSN = dfFilter[dfFilter["block"].isin(["SN"])]
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
                
        dfTmp = pd.DataFrame(data = datalist, columns=["Level","title","block","title_block"])
        dfTmp.sort_values(by=['title'])
        return dfTmp

    def language_processing(self, df:pd.DataFrame, nameFile: str) -> pd.DataFrame:
        # Get all title header
        titlesKey = pd.Series(list(dict.fromkeys(df["title"].to_list())))
        data = []
        for titleFR in titlesKey:
            # Filter set of data
            dfFilter = df[df["title"].isin([titleFR])]
            dfLanguage = dfFilter.loc[dfFilter["Level"] != 1]
            
            title_lang = ""
            title_lang = " ".join(str(x) for x in dfLanguage["title_block"].to_list())

            # Get language
            text = " ".join(title_lang.split())
            idLang = ""
            title_traduction = ""
            try:
                idLang = text.split()[0]
                if idLang in LANGUAGES:
                    title_traduction = " ".join(text.split(idLang))
                    idLang = LANGUAGE_DICT[idLang]
                else:
                    log.error("File: {} Title: {} Cannot found the language: {} ".format(nameFile,titleFR,title_lang))      
            except:
                idLang = ""
            
            if idLang is None:
                log.error("Cannot found laguage {}".format(title_lang))
            else:
                data.append([titleFR,idLang,title_traduction.lstrip()])            
        return pd.DataFrame(data = data, columns=["title","language","title_traduction"])

    def read_file(self) -> list:
        # Return a list with name of file and dataframe
        return self.readFileInput()
    