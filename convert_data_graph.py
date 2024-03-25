import os
import pandas as pd
from rdflib import Graph, URIRef, Namespace, Literal

class convert_graph:

    def __init__(self, dataset : list, outputDir) -> None:
        
        self.dataset = dataset
        self.output = outputDir
        self.jurivocGraph = Graph()

        # NameSpace
        self.jurivoc = Namespace("https://fedlex.data.admin.ch/vocabulary/jurivoc/")
        self.rdf = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
        self.skos = Namespace("http://www.w3.org/2004/02/skos/core#")
        self.dct = Namespace("http://purl.org/dc/terms/")
        self.owl = Namespace("http://www.w3.org/2002/07/owl#")
        self.jurivocGraph.bind("jurivoc",self.jurivoc)

    def generate_skos_concept(self, df:pd.DataFrame, nameGraph : str) -> Graph:
        # Create a Graph
        gConcepts = Graph()
        # Get all title header
        titles = df["title"].to_list()
        titlesKey = pd.Series(list(dict.fromkeys(titles)))
        for Title in titlesKey:
            if Title != "THÉSAURUS":
                # get block for each title
                dfFilter = df[df["title"].isin([Title])]
                # find if block contain USE
                block  = dfFilter["block"].to_list()            
                # If bExist is false then generate a skos:Concept
                if 'USE' not in block:
                    # Convert title to URI            
                    title_dq = self.dq_text(Title)
                    title_uri = URIRef(self.jurivoc + title_dq)
                    
                    # Create skos:Concept Graph
                    gConcepts.add((title_uri,self.rdf.type,self.skos.Concept))
                    gConcepts.add((title_uri,self.skos.inScheme,URIRef("https://fedlex.data.admin.ch/vocabulary/jurivoc")))
                    gConcepts.add((title_uri,self.skos.prefLabel,Literal(Title, lang="fr")))
                    gConcepts.add((title_uri,self.dct.identifier,Literal(title_dq, lang="fr")))
                    
                    for index, row in dfFilter.iterrows(): 
                        block = row["block"]
                        title_block = row["title_block"]

                        if (len(block) > 0) and (len(title_block) > 0):
                            # Generate Skos:altLabel
                            if block == "UF":
                                gConcepts.add((title_uri,self.skos.altLabel,Literal(title_block, lang="fr")))
                        
                            # Generate skos:broader and skos:narrower
                            if block == "BT":
                                if "THÉSAURUS" in title_block:
                                    gConcepts.add((title_uri,self.skos.topConceptOf,URIRef(self.jurivoc + self.dq_text("THÉSAURUS"))))
                                    gConcepts.add((URIRef(self.jurivoc + self.dq_text("THÉSAURUS")),self.skos.hasTopConcept,title_uri))

                                else:
                                    gConcepts.add((title_uri,self.skos.broader,URIRef(self.jurivoc + self.dq_text(title_block))))
                                    # Inverse to skos:broader
                                    gConcepts.add((URIRef(self.jurivoc + self.dq_text(title_block)),self.skos.narrower,title_uri))

                            # Generate skos:scopeNote
                            if block == "SN":
                                gConcepts.add((title_uri,self.skos.scopeNote,Literal(title_block, lang="fr") ))

                            if block == "SA":
                                gConcepts.add((title_uri,self.skos.related,URIRef(self.jurivoc + self.dq_text(title_block))))
        
        self.jurivocGraph += gConcepts
        return True
    
    def generate_Thesaurus(self,df:pd.DataFrame, nameGraph : str) -> Graph:

        # get block for each title
        gConceptScheme = Graph()
        dfFilter = df[df["title"].isin(["THÉSAURUS"])]
        if len(dfFilter) > 0:
            # Convert title to URI        
            title_uri = URIRef(self.jurivoc + "THESAURUS")
            # Create skos:Concept Graph
            gConceptScheme.add((title_uri,self.rdf.type,self.skos.ConceptScheme))
            gConceptScheme.add((title_uri,self.skos.prefLabel,Literal("THÉSAURUS", lang="fr")))

            for index,row in dfFilter.iterrows():
                block = row["block"]
                title_block = row["title_block"]

                # Generate skos:scopeNote
                if block == "SN":
                    gConceptScheme.add((title_uri,self.owl.versionInfo,Literal(title_block, lang="fr") ))        
        self.jurivocGraph += gConceptScheme
        return True    

    def generate_language_graph(self, df:pd.DataFrame) -> Graph:

        print("Save in graph # {} rows".format(len(df)))

        gLanguage = Graph()
        for index,row in df.iterrows():
            title = row["title"]
            title_uri = URIRef(self.jurivoc + self.dq_text(title))
            idLang = row["language"]
            title_language = row["title_traduction"]

            gLanguage.add((title_uri,self.skos.prefLabel,Literal(title_language, lang=idLang)))

        self.jurivocGraph += gLanguage
        return True

    def generate_graph_ger_ita(self,df:pd.DataFrame, nameFile) -> Graph:

        # Dataset Languages
        dftranslate = pd.DataFrame()
        for l in self.dataset:
            if "dbLanguage" in l[0]:
                dftranslate = l[1]
        
        #Merge
        
        dfinner = pd.merge(left=df, right=dftranslate, how='left', left_on='title', right_on='title_traduction')
        dfinner.columns = ['Level','title','block','title_block','title_translate','language','title_language']

        #dfinner.to_csv("Merge_traduction.csv",sep="|",index=False)
        
        gLanguage = Graph()

        # Get all title header
        titles = dfinner["title_translate"].to_list()
        titlesKey = pd.Series(titles).drop_duplicates().tolist()
        for Title in titlesKey:
            # get block for each title
            dfFilter = dfinner[dfinner["title_translate"].isin([Title])]
            # find if block contain USE
            block  = dfFilter["block"].to_list()
            bFlag = 'USE' in block
            if bFlag == False:
                
                title_uri = URIRef(self.jurivoc + self.dq_text(Title))
                title_lang = dfFilter["title"].unique()[0]
                idLang = dfFilter["language"].unique()[0]

                gLanguage.add((title_uri,self.skos.prefLabel,Literal(str(title_lang), lang=idLang)))
                for idx, row in dfFilter.iterrows():
                    if row["block"] == "UF":
                        titleBlock = row["title_block"]
                        gLanguage.add((title_uri,self.skos.altLabel,Literal(str(titleBlock),lang=idLang)))
                        
                    if row["block"] == "SN":
                        titleSN = row["title_block"]
                        gLanguage.add((title_uri,self.skos.scopeNote,Literal(str(titleSN),lang=idLang) ))                    
                
        #gLanguage.serialize(format="ttl", destination= "test.ttl")
        self.jurivocGraph += gLanguage
        return True
        
    def dq_text(self, title:str):

        data_input = title.upper()
        replace_dict = {"(":"_",")":"_","[":"_","]": "_","'":"_","\"":"_"," ":"_","-":"_","Ï":"_","¿":"_","½":"_","É":"E","È":"E","Ê":"E","À":"A","Ô":"O",".":"_",",":"_","Û":"U","Î":"I","Ç":"C"}

        #1. supprimer tous les caractères spéciaux, parenthèses, crochets, apostrophes, etc. : 
        #   les remplacer par “_”, garder seulement les lettres et les digits
        for old,new in replace_dict.items():
            data_input = data_input.replace(old,new)

        pTitle = list(data_input)
        TITLE_URI = ""
        if pTitle[-1] == "_":
            tlist = self.normalize_text_url(pTitle,-1)
            TITLE_URI = ''.join(tlist)        
        elif pTitle[0] == "_":
            tlist = self.normalize_text_url(pTitle,0)
            TITLE_URI = ''.join(tlist)
        else:
            TITLE_URI = data_input

        return TITLE_URI

    def normalize_text_url(self, split_title : list,ind : int):

        if split_title[ind] != "_":
            return split_title
        else:
            if ind == -1:
                split_title.pop((len(split_title)-1))
            if ind == 0:
                split_title.pop(0)
            self.normalize_text_url(split_title,ind)
        return split_title

    def graph_process(self)-> Graph:

        if not os.path.exists(self.output):
            os.mkdir(self.output)
        # read dataset
        for source in self.dataset:
            # Get source
            nameFile = source[0]
            df = source[1]

            if 'dbLanguage' in nameFile:
                print("Generate - Graph of Language {}".format("DB Language"))
                self.generate_language_graph(df)
            else:                
                if '_fre.txt' in nameFile:
                    print("Generate - Graph of data: {} # rows {}".format(nameFile, len(df)))
                    # =================== Graph THÉSAURUS
                    print("Graph THÉSAURUS")
                    self.generate_Thesaurus(df,nameFile) 
                    # =================== Graph Skos:Concept
                    print("Graph concepts")
                    self.generate_skos_concept(df,nameFile)                    
                
                if ('_ger.txt' in nameFile) or ('_ita.txt' in nameFile):
                    print("Generate - Graph of data: {}".format(nameFile))
                    self.generate_graph_ger_ita(df,nameFile)
        
        outputFile = file = os.path.join(self.output,'result.ttl')
        print("Created graph file {}".format(outputFile))
        
        return self.jurivocGraph.serialize(format="ttl", destination= outputFile)