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
        dfUpdate = self.update(dfTmp)
        dfOutput = self.processing_block_sn(dfUpdate)
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
                        title = " ".join(title_dataquality.split(block)).lstrip()                  
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

    def update(self,df:pd.DataFrame) -> pd.DataFrame:
        
        blockAux = ""

        # Evaluate and update dataframe
        indexMax = pd.Series(df["Level"].squeeze()).index.max()
        removeRow = []
        for index, row in df.iterrows():
            # Update title header
            if index < indexMax:
                Level_nextValue = df.at[index+1,"Level"]
                if row["Level"] == Level_nextValue:
                    if row["Level"] == 1:
                        # Update title
                        title = df.at[index,'title'] + ' ' + df.at[index+1,"title"]
                        df.at[index,'title'] = title
                        
                        ## Update concepts with title updated
                        df.loc[df['title'] == df.at[index+1,"title"], 'title'] = title

                        # Drop index not necessary
                        removeRow.append(index+1)

        # Remove rows 
        dfTemp = df.drop(removeRow)
        # Reset index DataFrame
        dfTemp.reset_index()

        # 
        blockAux = ""
        for index,row in dfTemp.iterrows():
            nLevel = row["Level"]
            block =  row["block"]            
            if nLevel != 1:
                if block:
                    # Get block Id
                    blockAux = block
                else:
                    dfTemp.at[index,"block"] = blockAux 
        
        # Process when Block is SN 
        #dfOutput = self.processing_block_sn(dfTemp)        
        return dfTemp

    def processing_block_sn(self,df:pd.DataFrame):
        
        titles = list(dict.fromkeys(df["title"].to_list()))
        data = []
        for title in titles:
            # Get Dataframe block from title id
            dfFilter = df[df["title"].isin([title])]
            blocks = list(dict.fromkeys(dfFilter["block"].to_list()))
            if 'SN' in blocks:
                #Filter SN in Dataframe 
                dfFilterSN = dfFilter[dfFilter["block"].isin(["SN"])]
                if len(dfFilterSN) > 1:
                    str_note = " ".join(str(x) for x in dfFilterSN["title_block"].to_list())

                    # Find row with SN block Status
                    idx = dfFilter[dfFilter["block"]=="SN"].index
                    rowSN = idx.min()
                    # Update title bloc with SN status
                    dfFilter.at[rowSN,"title_block"] = str_note                    
                    # Remove all row with SN status
                    nexIdx = idx.drop(rowSN)
                    tmp = dfFilter.drop(nexIdx)

                    data.append(tmp)
                else: 
                    data.append(dfFilter)
            else:
                data.append(dfFilter)
        
        return pd.concat(data,ignore_index=True)

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
            
            #print("Title {} language {} traduction {} ".format(titleFR,idLang,title_traduction))
            if idLang is None:
                log.error("Cannot found laguage {}".format(title_lang))
            else:
                data.append([titleFR,idLang,title_traduction.lstrip()])            
        return pd.DataFrame(data = data, columns=["title","language","title_traduction"])

    def read_file(self) -> list:
        # Return a list with name of file and dataframe
        return self.readFileInput()
    