import os
import pandas as pd
import numpy as np
from rdflib import Graph, URIRef, Namespace, Literal
from rdflib.collection import Collection
from rdflib.term import BNode
import glob
from rdflib.paths import Path, eval_path
#from nltk.corpus import wordnet as wn

# Declaration Global NAMESPACE
ns_jurivoc = Namespace("https://fedlex.data.admin.ch/vocabulary/jurivoc/")
ns_rdf = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
ns_rdfs = Namespace("http://www.w3.org/2000/01/rdf-schema#")
ns_skos = Namespace("http://www.w3.org/2004/02/skos/core#")
ns_dct = Namespace("http://purl.org/dc/terms/")
ns_owl = Namespace("http://www.w3.org/2002/07/owl#")
ns_madsrdf = Namespace("http://www.loc.gov/mads/rdf/v1#")


class update_graph:

    def __init__(self, graphInput : Graph, pathGraph : str) -> None:
        self.graphCurrent = Graph()
        self.graphNew = graphInput
        self.graphNew.bind("jurivoc",ns_jurivoc)
        self.directory = pathGraph

        if os.path.exists(pathGraph):
            if os.path.isfile(pathGraph):
                self.graphCurrent.parse(pathGraph)
            else:
                if os.path.isdir(pathGraph):
                    for f in os.listdir(pathGraph):
                        fileInput = os.path.join(pathGraph, f)
                        if os.path.isfile(fileInput):

                            self.graphCurrent.parse(fileInput)

    def generate_new_URIS(self) -> Graph:

        newURIs = []
        # Generate new URI
        for sConcept,pConcept,oConcept in self.graphNew.triples((None,None,ns_skos.Concept)):
            newURIs.append([sConcept,sConcept.split("/")[-1]])
        dfURIS = pd.DataFrame(data=newURIs,columns=["uri","title"])
        dfURIS.sort_values(by=["title"], inplace=True)
        dfURIS.reset_index(drop=True, inplace=True)
        dfURIS["newURI"] = [str(idx+1) for idx,row in dfURIS.iterrows()]
        #dfURIS.to_csv("newUris.csv",sep="|",index=False)
        # Update URIS
        for index, row in dfURIS.iterrows():
            subject_uri = row["uri"]
            newURI = URIRef(ns_jurivoc + row["newURI"])
           
            if (subject_uri,None,None) in self.graphNew:
                for s,p,o in self.graphNew.triples((subject_uri,None,None)):
                    self.graphNew.add((newURI,p,o))
                    # Update identifier
                    self.graphNew.set((newURI,ns_dct.identifier,Literal(newURI.split('/')[-1])))
                self.graphNew.remove((subject_uri,None,None))
                                
                if (None,None,subject_uri) in self.graphNew:
                    for s,p,o in self.graphNew.triples((None,None,subject_uri)):
                        self.graphNew.add((s,p,newURI))
                    self.graphNew.remove((None,None,subject_uri))
                else:
                    print("Warning: no triples found with {} as object".format(subject_uri))
            else:
                print("Warning: no triples found with {} as subject".format(subject_uri))
        return True
    
    def get_lang(self, text) -> str:
        language = ""
        # language
        if isinstance(text[1], Literal):
            if text[1].language is not None:
                language = '@'+f"{text[1].language}"
            else:
                language = ""
        else:
            language = ""
        return language
    
    def get_alt_label(self,subject,g:Graph) -> list:

        list_AltLabel = []
            
        listOfAltLabel = list(eval_path(g,
                                (subject,ns_skos.altLabel,None)
                                ))
        [list_AltLabel.append([al[0],al[1]+self.get_lang(al)]) for al in listOfAltLabel]

        return list_AltLabel

    def get_pref_label(self,subject,g:Graph) -> list:
        
        prefLabel = []
        listOfPrefLabel = list(eval_path(g,
                                (subject,ns_skos.prefLabel,None)
                                ))
        [prefLabel.append([al[0],al[1]+self.get_lang(al)]) for al in listOfPrefLabel]

        return prefLabel

    def update_old_new_graph(self):

        # Get all data in the new Graph
        dfNew = [[s,self.get_alt_label(s,self.graphNew),self.get_pref_label(s,self.graphNew) ] for s,p,o in self.graphNew]

        # Get all data in the Old Graph
        dfNew = [[s,self.get_alt_label(s,self.graphNew),self.get_pref_label(s,self.graphNew) ] for s,p,o in self.graphNew]

        print(dfNew)

    def get_predicate_altLabe_prefLabel(self, gProcess) -> pd.DataFrame:

        list_AltLabel = []
        list_PrefLabel = []
        for s,p,o in gProcess.triples((None,None,ns_skos.Concept)):            
            
            listOfAltLabel = list(eval_path(gProcess,
                                    (s,ns_skos.altLabel,None)
                                    ))
            [list_AltLabel.append([al[0],al[1]+self.get_lang(al)]) for al in listOfAltLabel]
            #test = []
            #[list_AltLabel.append(self.read_data(l)) for l in listOfAltLabel]
            #[print("Type Input {} result {}".format(type(l),self.read_data(l))) for l in listOfAltLabel]
            
            listOfPrefLabel = list(eval_path(gProcess,
                                    (s,ns_skos.prefLabel,None)
                                    ))
            #[list_PrefLabel.append(self.read_data(pl)) for pl in listOfPrefLabel]
            [list_PrefLabel.append([pl[0],pl[1]+self.get_lang(pl)]) for pl in listOfPrefLabel]

        dfAlt = pd.DataFrame(data=list_AltLabel, columns=['uri','description'])
        dfPref = pd.DataFrame(data=list_PrefLabel, columns=['uri','description'])
        # Merge the alt and pref lables in a dataframe only
        dfMerge = dfAlt # + dfPref #pd.merge(dfAlt,dfPref,on="uri") #dfAlt.merge(dfPref,left_on="uri",right_on="uri")
        return dfAlt,dfPref,dfMerge
    
    def update_graph_subject(self, df:pd.DataFrame):

        df.to_csv("match.csv",sep="|",index=False)
        uriKey = pd.Series(df['uri'].to_list()).drop_duplicates().to_list()
        # Update Subject
        for uri_source in uriKey:
            uriOld = df[df['uri'].isin([uri_source])]['uri_old'].to_list()
            uniqueURI = pd.Series(uriOld).drop_duplicates().to_list()
            uri_current = ",".join(uniqueURI)
            if len(uniqueURI) > 1:
                print("1")
                #logging.warning("Error in {} uri with cannot possible 2 uris with the same data {} uris".format(uri_source,",".join(uri_current)))
            for s,p,o in self.graphNew.triples((uri_source,None,None)):
                uri_new = URIRef(str(uri_current))
                self.graphNew.add((uri_new,p,o))
                self.graphNew.set((uri_new,ns_dct.identifier,Literal(uri_new.split('/')[-1])))
            self.graphNew.remove((uri_source,None,None))
        return True
    
    def match_uri_update(self,dfNew:pd.DataFrame,dfOld:pd.DataFrame):

        dfMerge = pd.merge(dfNew,dfOld,how='inner', left_on=['description'], right_on=['description'])
        dfUpdate = dfMerge.rename({'uri_x': 'uri', 'uri_y': 'uri_old'}, axis='columns')
        self.update_graph_subject(dfUpdate)

        return True
    
    def compare_graph_get_uri(self) -> Graph:
        
        # Get Data value URI, LABELS
        dfGraphNew_Alt,dfGraphNew_Pref,dfNew = self.get_predicate_altLabe_prefLabel(self.graphNew)
        dfNew.sort_values(by=["uri"], inplace=True)
        #dfGraphNew_Alt.to_csv('altLabel_1.csv',sep="|",index=False)
        #dfGraphNew_Pref.to_csv('prefLabel_1.csv',sep="|",index=False)
        #dfNew.to_csv('newGraph_1.csv',sep="|",index=False)
        dfGraphOld_Alt,dfGraphOld_Pref,dfOld = self.get_predicate_altLabe_prefLabel(self.graphCurrent)
        #dfOld.sort_values(by=["uri"], inplace=True)
        #dfGraphNew_Alt.to_csv('altLabel_2.csv',sep="|",index=False)
        #dfGraphNew_Pref.to_csv('prefLabel_2.csv',sep="|",index=False)
        #dfOld.to_csv('oldGraph.csv',sep="|",index=False)

        # Etape 1 - Matche all URI
        self.match_uri_update(dfNew,dfOld)
        
        return True

    def update_uri_concepts(self):
        if len(self.graphCurrent) > 0:
            # update the UTIS between graph current and new graph
            print("Update graphs with old graph")
            gOutput = self.compare_graph_get_uri()            
        else:
            print("Generate new URIs in Skos:Concept")
            # Generate URIS in the Graph Concepts
            self.generate_new_URIS()            
        return self.graphNew


class convert_graph:

    def __init__(self, dataset : list, outputDir) -> None:
        
        self.dataset = dataset
        self.output = outputDir
        self.jurivocGraph = Graph()

        self.jurivocGraph.bind("jurivoc",ns_jurivoc)
        self.jurivocGraph.bind("madsrdf",ns_madsrdf)
        self.jurivocGraph.bind("skos",ns_skos)
        self.jurivocGraph.bind("owl",ns_owl)
        self.jurivocGraph.bind("owl",ns_owl)

    def generate_skos_concept(self, df:pd.DataFrame, titlekey:list) -> Graph:
        # Create a Graph
        
        gConcepts = Graph()
        
        for Title in titlekey:
            if len(Title) > 0:
                # get block for each title
                dfFilter = df[df["title"].isin([Title])]
                # find if block contain USE
                block  = dfFilter["block"].to_list()
                # If bExist is false then generate a skos:Concept
                if 'USE' not in block:
                    # Convert title to URI       
                    print('Title {}'.format(Title) )     
                    title_dq = self.dataquality_text(Title)
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
                                    gConcepts.add((title_uri,ns_skos.topConceptOf,URIRef("https://fedlex.data.admin.ch/vocabulary/jurivoc")))
                                    gConcepts.add((URIRef("https://fedlex.data.admin.ch/vocabulary/jurivoc"),ns_skos.hasTopConcept,title_uri))
                                else:
                                    gConcepts.add((title_uri,ns_skos.broader,URIRef(ns_jurivoc + self.dataquality_text(title_block))))
                                    # Inverse to skos:broader
                                    gConcepts.add((URIRef(ns_jurivoc + self.dataquality_text(title_block)),ns_skos.narrower,title_uri))

                            # Generate skos:scopeNote
                            if block == "SN":
                                gConcepts.add((title_uri,ns_skos.scopeNote,Literal(title_block, lang="fr") ))

                            if block == "SA":
                                gConcepts.add((title_uri,ns_skos.related,URIRef(ns_jurivoc + self.dataquality_text(title_block))))
                                gConcepts.add((URIRef(ns_jurivoc + self.dataquality_text(title_block)),ns_skos.related,title_uri))
            
        self.jurivocGraph += gConcepts
        return True
    
    def generate_Thesaurus(self,df:pd.DataFrame) -> Graph:

        # get block for each title
        gConceptScheme = Graph()
        # Convert title to URI        
        title_uri = URIRef("https://fedlex.data.admin.ch/vocabulary/jurivoc")
        # Create skos:Concept Graph
        gConceptScheme.add((title_uri,ns_rdf.type,ns_skos.ConceptScheme))
        gConceptScheme.add((title_uri,ns_skos.prefLabel,Literal("THÉSAURUS", lang="fr")))
        for index,row in df.iterrows():
            block = row["block"]
            title_block = row["title_block"]
            # Generate skos:scopeNote
            if block == "SN":
                gConceptScheme.add((title_uri,ns_owl.versionInfo,Literal(title_block) ))
        self.jurivocGraph += gConceptScheme
        return True

    def generate_madsrdf(self, df:pd.DataFrame, titlekey:list) -> Graph:

        gSpecific = Graph()
        log_df = []
        for title in titlekey:
            # Get block
            dfTitle = df[df["title"].isin([title])]

            blocks = pd.Series(dfTitle["title"].to_list()).drop_duplicates().to_list()
            if "USE" not in blocks:
                title_dq = self.dataquality_text(title)
                title_uri = URIRef(ns_jurivoc+title_dq)

                gSpecific.add((title_uri,ns_rdf.type,URIRef(ns_madsrdf.ComplexSubject)))
                gSpecific.add((title_uri,ns_madsrdf.authoritativeLabel,Literal(title,lang="fr")))

                datacomponentList = []
                for idx, row in dfTitle.iterrows():

                    if row["block"] == "USA":
                        titleBlock = self.dataquality_text(row["title_block"])
                        uriComponent = URIRef(ns_jurivoc+titleBlock)
                        datacomponentList.append(uriComponent)
                        #
                        gSpecific.add((uriComponent,ns_rdfs.seeAlso,title_uri))
                    
                    if row["block"] == "AND":
                        titleBlock = self.dataquality_text(row["title_block"])
                        uriComponent = URIRef(ns_jurivoc+titleBlock)
                        datacomponentList.append(uriComponent)
                        #
                        gSpecific.add((uriComponent,ns_rdfs.seeAlso,title_uri))

                if len(datacomponentList) > 0:
                    nodeList = BNode()
                    gSpecific.add((title_uri,ns_madsrdf.componentList,nodeList))
                    Collection(gSpecific,nodeList,datacomponentList)                
            else:
                print("Warning: the {} title contain a block USE".format(title))
                log_df.append([dfTitle])
            
        self.jurivocGraph += gSpecific
        return True

    def generate_language_graph(self, df:pd.DataFrame) -> Graph:

        print("Save in graph # {} rows".format(len(df)))

        gLanguage = Graph()
        for index,row in df.iterrows():
            title = row["title"]
            title_uri = URIRef(ns_jurivoc + self.dataquality_text(title))
            idLang = row["language"]
            
            title_language = row["title_traduction"]

            gLanguage.add((title_uri,ns_skos.prefLabel,Literal(title_language, lang=idLang)))

        self.jurivocGraph += gLanguage
        return True

    def generate_graph_ger_ita(self,df:pd.DataFrame, nameFile) -> Graph:

        print('Language {}'.format(nameFile))
        # Dataset Languages
        dftranslate = pd.DataFrame()
        for l in self.dataset:
            if "dbLanguage" in l[0]:
                dftranslate = l[1]

        if 'jurivoc_ger' in nameFile:
            keyLanguage = 'de'
        
        if 'jurivoc_ita' in nameFile:
            keyLanguage = 'it'
        
        #dfLanguage = dftranslate[dftranslate['level'] > 1]
        dfMerge = pd.merge(left=df, right=dftranslate, how='inner', left_on='title', right_on='title_traduction')
        dfMerge.columns = ['level','title','block','title_block','title_translate','language','title_language']
        dfTmp = dfMerge[dfMerge['level'] != 1]
        dfinner = dfTmp.reset_index(drop=True)

        print('Language Filter: {} '.format(keyLanguage))
        dfDB = dfinner[dfinner['language'].isin([keyLanguage])]
        #dfDB.to_csv('filter.csv',sep='|',index=False)

        #dfinner.to_csv("Merge_traduction.csv",sep="|",index=False)        
        gLanguage = Graph()

        # Get all title header
        titles = dfDB["title_translate"].to_list()
        titlesKey = pd.Series(titles).drop_duplicates().tolist()
        for Title in titlesKey:
            # get block for each title
            dfFilter = dfDB[dfDB["title_translate"].isin([Title])]
            # find if block contain USE
            block  = dfFilter["block"].to_list()
            bFlag = 'USE' in block
            if bFlag == False:
                
                title_uri = URIRef(ns_jurivoc + self.dataquality_text(Title))
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
        
    def dataquality_text(self, title:str):

        data_input = title.upper()
        replace_dict = {"(":"_",")":"_","[":"_","]": "_","'":"_","\"":"_"," ":"_","-":"_","Ï":"_","¿":"_","½":"_","É":"E","È":"E","Ê":"E","À":"A","Â":"A","Ô":"O",".":"_",",":"_","Û":"U","Î":"I","Ç":"C","/":"_"}

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

    def get_specific_usa_and(self,df:pd.DataFrame, titlesKey:list) -> pd.DataFrame:
        list_tmp = []
        for title in titlesKey:
            # Filter df
            dfFilter = df[df["title"].isin([title])]
            #
            blocks = pd.Series(dfFilter["block"].to_list()).drop_duplicates().to_list()
            if ('USA' in blocks) or ('AND' in blocks):
                    list_tmp.append(dfFilter)
        
        dfTmp = pd.concat(list_tmp,ignore_index=True)
        dfTmp.reset_index()
        return dfTmp

    def graph_process(self)-> Graph:

        # read dataset
        for source in self.dataset:
            # Get source
            nameFile = source[0]
            df = source[1]

            print('file name: {}'.format(nameFile))

            if 'dbLanguage' in nameFile:
                #logging.info("Generate - Graph of Language {}".format("DB Language"))
                print("Generate - Graph of Language {}".format("DB Language"))
                self.generate_language_graph(df)
            else:                
                if '_fre' in nameFile:

                    titlesKey = pd.Series(df["title"].to_list()).drop_duplicates().to_list()
                    
                    # USA and AND block specific Data
                    dfSpecific = self.get_specific_usa_and(df,titlesKey)
                    dfSpecific.to_csv("data_usa_and.csv",sep="|",index=False)

                    #logging.info("Graph of data: {} # rows {}".format(nameFile, len(df)))
                    # =================== Graph THÉSAURUS
                    #logging.info("Graph THÉSAURUS")
                    dfTHESAURUS = df[df["title"] == "THÉSAURUS"]
                    self.generate_Thesaurus(dfTHESAURUS) 
                    print("Thesaurus")
                    # =================== Graph Skos:Concept
                    #logging.info("Graph skos:Concepts")
                    titleKey_not_Concept = pd.Series(dfSpecific["title"].to_list()).drop_duplicates().to_list()
                    titleKey_not_Concept.append("THÉSAURUS")
                    
                    dfConcept = df[~df["title"].isin(titleKey_not_Concept)]
                    
                    dfConcept.to_csv("data_concepts.csv",sep="|",index=False)
                    titlesKeyConcept = pd.Series(dfConcept["title"].to_list()).drop_duplicates().to_list()
                    self.generate_skos_concept(dfConcept,
                                               titlesKeyConcept
                                               )
                    print("Concepts")
                    # =================== Graph Specific blocks
                    #logging.info("Graph specific USA and AND block")
                    self.generate_madsrdf(dfSpecific,
                                              pd.Series(dfSpecific["title"].to_list()).drop_duplicates().to_list()
                                              )        
                    print("madsrdf")                
                if ('jurivoc_ger' in nameFile) or ('jurivoc_ita' in nameFile):
                    #logging.info("Generate - Graph of data: {}".format(nameFile))
                    print('Generate Graph: {}'.format(nameFile))
                    self.generate_graph_ger_ita(df,nameFile)
        
        return self.jurivocGraph