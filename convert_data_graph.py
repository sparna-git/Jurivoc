import os
import pandas as pd
from rdflib import Graph, URIRef, Namespace, Literal

# Declaration Global
ns_jurivoc = Namespace("https://fedlex.data.admin.ch/vocabulary/jurivoc/")
ns_thesaurus = Namespace("https://fedlex.data.admin.ch/vocabulary/jurivoc#")
ns_rdf = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
ns_skos = Namespace("http://www.w3.org/2004/02/skos/core#")
ns_dct = Namespace("http://purl.org/dc/terms/")
ns_owl = Namespace("http://www.w3.org/2002/07/owl#")

class update_graph:

    def __init__(self, graphInput, pathGraph) -> None:
        self.graphCurrent = Graph()
        self.graphNew = Graph()
        self.graphNew.bind("jurivoc",ns_jurivoc)
        
        # Graph New
        gInput = Graph()
        print("Size graph: {}".format(str(len(gInput.parse(graphInput)))))
        self.graphNew += gInput.parse(graphInput)
        
        # Graph Current
        self.graphCurrent.parse(pathGraph)
                
    def findURI(self,uris:list,value):
        
        for l in uris:
            if l[0] == value:
                return l[1]
                break
        return True

    def generate_new_URIS(self) -> Graph:

        gConcept = Graph()
        newURIs = []
        # Generate new URI
        URI_Id = 1
        for sConcept,pConcept,oConcept in self.graphNew.triples((None,ns_rdf.type,ns_skos.Concept)):
            new_uri = URIRef(ns_jurivoc+str(URI_Id))
            newURIs.append([sConcept,new_uri])
            URI_Id += 1

        #Navigatin in the Graph
        # Generate Nodes
        for sConcept,pConcept,oConcept in self.graphNew.triples((None,ns_rdf.type,ns_skos.Concept)):
            # Generate new Graph
            new_uri = self.findURI(newURIs,sConcept)
            # Generate triple Skos:Concept
            gConcept.add((new_uri,ns_rdf.type,ns_skos.Concept))
        # Generate Properties
        for sConcept,pConcept,oConcept in self.graphNew.triples((None,ns_rdf.type,ns_skos.Concept)):            
            # Get all predicates
            new_uri = self.findURI(newURIs,sConcept)
            predicates = self.graphNew.predicates(sConcept,unique=True)
            for p in predicates:
                for su,pr,ob in self.graphNew.triples((sConcept,p,None)):
                    if str(pr) == "http://purl.org/dc/terms/identifier":
                        URI_Id = new_uri.split("/")[-1]
                        gConcept.add((new_uri,pr,Literal(URI_Id)))
                    elif str(pr) == "http://www.w3.org/2004/02/skos/core#broader":
                        try:
                            new_uri_broader = self.findURI(newURIs,ob)
                            if new_uri_broader:
                                gConcept.add((new_uri,pr,new_uri_broader))
                        except:
                            print("Warning: Subject {}, the uri {} broader is not found a relation ".format(sConcept,ob))
                            gConcept.add((new_uri,pr,ob))
                    elif str(pr) == "http://www.w3.org/2004/02/skos/core#narrower":
                        try:
                            new_uri_narrower = self.findURI(newURIs,ob)
                            if new_uri_narrower:
                                gConcept.add((new_uri,pr,new_uri_narrower))
                        except:
                            print("Warning: Subject {}, the uri {} narrower is not found a relation ".format(sConcept,ob))
                            gConcept.add((new_uri,pr,ob))
                    elif str(pr) == "http://www.w3.org/2004/02/skos/core#related":
                        try:
                            new_uri_related = self.findURI(newURIs,ob)
                            if new_uri_related:
                                gConcept.add((new_uri,pr,new_uri_related))
                        except:
                            print("Warning: Subject {}, the uri {} related is not found a relation ".format(sConcept,ob))
                            gConcept.add((new_uri,pr,ob))
                    else:
                        gConcept.add((new_uri,pr,ob))
                    self.graphNew.remove((su,pr,ob))
            self.graphNew.remove((sConcept,pConcept,oConcept))

        # Thesaurus
        gThesaurus = Graph()
        for s,p,o in self.graphNew.triples((None,None,ns_skos.ConceptScheme)):
            gThesaurus.add((s,p,o))
            for su,pr,ob in self.graphNew.triples((s,ns_skos.hasTopConcept,None)):
                try:
                    new_uri = self.findURI(newURIs,ob)
                    if len(new_uri) > 0:
                        gThesaurus.add((s,pr,new_uri))
                except:
                    print("The {} uri, cannot found in the relation".format(ob))
                    gThesaurus.add((s,pr,ob))
                self.graphNew.remove((su,pr,ob))    
        self.graphNew.remove((s,p,o))
        
        self.graphNew += gConcept + gThesaurus
        return self.graphNew

    def update_graphs(self) -> Graph:

        for s,p,o in self.graphNew.triples((None,ns_rdf.type,ns_skos.Concept)):

            altLabel = []
            prefLabel = []

            [altLabel.append(oAL) for sAL,pAL,oAL in self.graphNew.triples((s,ns_skos.altLabel,None))]
            [altLabel.append(oAL) for sAL,pAL,oAL in self.graphNew.triples((s,ns_skos.prefLabel,None))]

            

            if str(s) == 'https://fedlex.data.admin.ch/vocabulary/jurivoc/ECHANGE_DE_PERMIS':
                print(s)

                altlabel_values = self.graphNew.objects(s,ns_skos.altLabel, unique=False)
                preflabel_values = self.graphNew.objects(s,ns_skos.prefLabel, unique=False)

                print('|'.join(map(str, altlabel_values)))
                print('*'.join(map(str, preflabel_values)))

        return True
    
    #def find_uri_graph(self,subject,altlabel_value:list,preflabel_value:list) -> str:




    def update_uri_concepts(self):

        if len(self.graphCurrent) > 0:
            # update the UTIS between graph current and new graph
            print("Update graphs")
            self.update_graphs()
        else:
            print("Generate new URIs in Skos:Concept")
            # Generate URIS in the Graph Concepts
            gOutput = self.generate_new_URIS()
            # Generated output
            gOutput.serialize(format="ttl", destination= "result_Output.ttl")
        return True


class convert_graph:

    def __init__(self, dataset : list, outputDir) -> None:
        
        self.dataset = dataset
        self.output = outputDir
        self.jurivocGraph = Graph()

        self.jurivocGraph.bind("jurivoc",ns_jurivoc)
        self.jurivocGraph.bind("thesaurus",ns_thesaurus)

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
                    title_uri = URIRef(ns_jurivoc + title_dq)
                    
                    # Create skos:Concept Graph
                    gConcepts.add((title_uri,ns_rdf.type,ns_skos.Concept))
                    gConcepts.add((title_uri,ns_skos.inScheme,URIRef('https://fedlex.data.admin.ch/vocabulary/jurivoc')))
                    gConcepts.add((title_uri,ns_skos.prefLabel,Literal(Title, lang="fr")))
                    gConcepts.add((title_uri,ns_dct.identifier,Literal(title_dq)))
                    
                    for index, row in dfFilter.iterrows(): 
                        block = row["block"]
                        title_block = row["title_block"]

                        if (len(block) > 0) and (len(title_block) > 0):
                            # Generate Skos:altLabel
                            if block == "UF":
                                gConcepts.add((title_uri,ns_skos.altLabel,Literal(title_block, lang="fr")))
                        
                            # Generate skos:broader and skos:narrower
                            if block == "BT":
                                if "THÉSAURUS" in title_block:
                                    gConcepts.add((title_uri,ns_skos.topConceptOf,URIRef(ns_thesaurus + self.dq_text("THÉSAURUS"))))
                                    gConcepts.add((URIRef(ns_thesaurus + self.dq_text("THÉSAURUS")),ns_skos.hasTopConcept,title_uri))

                                else:
                                    gConcepts.add((title_uri,ns_skos.broader,URIRef(ns_jurivoc + self.dq_text(title_block))))
                                    # Inverse to skos:broader
                                    gConcepts.add((URIRef(ns_jurivoc + self.dq_text(title_block)),ns_skos.narrower,title_uri))

                            # Generate skos:scopeNote
                            if block == "SN":
                                gConcepts.add((title_uri,ns_skos.scopeNote,Literal(title_block, lang="fr") ))

                            if block == "SA":
                                gConcepts.add((title_uri,ns_skos.related,URIRef(ns_jurivoc + self.dq_text(title_block))))
        
        self.jurivocGraph += gConcepts
        return True
    
    def generate_Thesaurus(self,df:pd.DataFrame, nameGraph : str) -> Graph:

        # get block for each title
        gConceptScheme = Graph()
        dfFilter = df[df["title"].isin(["THÉSAURUS"])]
        if len(dfFilter) > 0:
            # Convert title to URI        
            title_uri = URIRef(ns_thesaurus + "THESAURUS")
            # Create skos:Concept Graph
            gConceptScheme.add((title_uri,ns_rdf.type,ns_skos.ConceptScheme))
            gConceptScheme.add((title_uri,ns_skos.prefLabel,Literal("THÉSAURUS", lang="fr")))

            for index,row in dfFilter.iterrows():
                block = row["block"]
                title_block = row["title_block"]

                # Generate skos:scopeNote
                if block == "SN":
                    gConceptScheme.add((title_uri,ns_owl.versionInfo,Literal(title_block) ))        
        self.jurivocGraph += gConceptScheme
        return True    

    def generate_language_graph(self, df:pd.DataFrame) -> Graph:

        print("Save in graph # {} rows".format(len(df)))

        gLanguage = Graph()
        for index,row in df.iterrows():
            title = row["title"]
            title_uri = URIRef(ns_jurivoc + self.dq_text(title))
            idLang = row["language"]
            title_language = row["title_traduction"]

            gLanguage.add((title_uri,ns_skos.prefLabel,Literal(title_language, lang=idLang)))

        self.jurivocGraph += gLanguage
        return True

    def generate_graph_ger_ita(self,df:pd.DataFrame, nameFile) -> Graph:

        # Dataset Languages
        dftranslate = pd.DataFrame()
        for l in self.dataset:
            if "dbLanguage" in l[0]:
                dftranslate = l[1]
        
        #Merge
        
        dfinner = pd.merge(left=df, right=dftranslate, how='inner', left_on='title', right_on='title_traduction')
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
                
                title_uri = URIRef(ns_jurivoc + self.dq_text(Title))
                title_lang = dfFilter["title"].unique()[0]
                idLang = dfFilter["language"].unique()[0]

                gLanguage.add((title_uri,ns_skos.prefLabel,Literal(str(title_lang), lang=idLang)))
                for idx, row in dfFilter.iterrows():
                    if row["block"] == "UF":
                        titleBlock = row["title_block"]
                        gLanguage.add((title_uri,ns_skos.altLabel,Literal(str(titleBlock),lang=idLang)))
                        
                    if row["block"] == "SN":
                        titleSN = row["title_block"]
                        gLanguage.add((title_uri,ns_skos.scopeNote,Literal(str(titleSN),lang=idLang) ))                    
                
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
        self.jurivocGraph.serialize(format="ttl", destination= outputFile)

        return self.jurivocGraph