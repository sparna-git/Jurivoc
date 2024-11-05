import os
import pandas as pd
from rdflib import Graph, URIRef, Namespace, Literal
from rdflib.collection import Collection
from rdflib.term import BNode
#https://rdflib.readthedocs.io/en/stable/_modules/rdflib/paths.html
from rdflib.paths import Path, evalPath
from rdflib.term import BNode


# Save data log
wlog_block = []

# Declaration Global NAMESPACE
ns_jurivoc = Namespace("https://jurivoc.bger.ch/vocabulary/jurivoc/")
ns_rdf = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
ns_rdfs = Namespace("http://www.w3.org/2000/01/rdf-schema#")
ns_skos = Namespace("http://www.w3.org/2004/02/skos/core#")
ns_dct = Namespace("http://purl.org/dc/terms/")
ns_owl = Namespace("http://www.w3.org/2002/07/owl#")
ns_madsrdf = Namespace("http://www.loc.gov/mads/rdf/v1#")

def dataquality_text(title:str):

    data_input = title.upper()
    replace_dict = {"(":"_",")":"_","[":"_","]": "_","'":"_","\"":"_"," ":"_","Ï":"_","¿":"_","½":"_","É":"E","È":"E","Ê":"E","À":"A","Â":"A","Ô":"O",".":"_",",":"_","Û":"U","Î":"I","Ç":"C","/":"_","&":"_"}

    #1. supprimer tous les caractères spéciaux, parenthèses, crochets, apostrophes, etc. : 
    #   les remplacer par “_”, garder seulement les lettres et les digits
    for old,new in replace_dict.items():
        data_input = data_input.replace(old,new)

    pTitle = list(data_input)
    TITLE_URI = ""        
    if pTitle[-1] == "_":
        tlist = normalize_text_url(pTitle,-1)
        TITLE_URI = ''.join(tlist)        
    elif pTitle[0] == "_":
        tlist = normalize_text_url(pTitle,0)
        TITLE_URI = ''.join(tlist)
    else:
        TITLE_URI = data_input

    return TITLE_URI

def normalize_text_url(split_title : list,ind : int):

    if split_title[ind] != "_":
        return split_title
    else:
        if ind == -1:
            split_title.pop((len(split_title)-1))
        if ind == 0:
            split_title.pop(0)
        normalize_text_url(split_title,ind)
    return split_title

def remove_c_title(title:str):

    import re
    if re.match('^(C_)([0-9]+)$',title):
        stitle = title.replace('C_','')
    else:
        stitle = title

    return stitle


class update_graph:

    def __init__(self, graphInput : Graph, pathGraph : str, dirlog : str, noComplexSubjects:bool) -> None:
        self.graphCurrent = Graph()
        self.graphNew = graphInput
        self.graphNew.bind("jurivoc",ns_jurivoc)

        self.noComplexSubjects = noComplexSubjects

        dir_data_for_graph = os.path.join(dirlog,'data_for_graph')
        isExiste = os.path.exists(dir_data_for_graph)
        if isExiste == False:
            os .makedirs(dir_data_for_graph)     
            self.logs = dir_data_for_graph       
        else:    
            self.logs = dir_data_for_graph

        self.directory = pathGraph     
        if os.path.exists(pathGraph):
            tmpGraph = Graph()
            if os.path.isfile(pathGraph):
                with open(pathGraph, "r") as f:
                    tmpGraph.parse(pathGraph,publicID ='https://jurivoc.bger.ch/vocabulary/jurivoc/',format="n3")
            else:
                if os.path.isdir(pathGraph):
                    for f in os.listdir(pathGraph):
                        fileInput = os.path.join(pathGraph, f)
                        if os.path.isfile(fileInput):
                            with open(fileInput,'r') as f:
                                tmpGraph.parse(f,publicID ='https://jurivoc.bger.ch/vocabulary/jurivoc/' ,format="n3")
            gSerializeN3 = tmpGraph.serialize(format="n3").decode('utf-8')
            self.graphCurrent.parse(data=gSerializeN3,format="n3")
            
            # Get Id Concept
            nSeq = []
            [nSeq.append(s.split('/')[-1]) for s,p,o in self.graphCurrent.triples((None,None,ns_skos.Concept))]
            self.IdSeq = nSeq
            # Get Id ComplexSubject
            ComplexSubjectURI = []
            [ComplexSubjectURI.append(s.split('/')[-1].split('_')[0]) for s,p,o in self.graphCurrent.triples((None,None,ns_madsrdf.ComplexSubject))]
            self.ComplexSubjectID = ComplexSubjectURI

    def generate_new_URIS(self) -> Graph:

        newURIs = []
        # Generate new URI
        for sConcept,pConcept,oConcept in self.graphNew.triples((None,None,ns_skos.Concept)):
            newURIs.append([sConcept,sConcept.split("/")[-1]])
        dfURIS = pd.DataFrame(data=newURIs,columns=["uri","title"])
        dfURIS.sort_values(by=["title"], inplace=True)
        dfURIS.reset_index(drop=True, inplace=True)
        dfURIS["newURI"] = [str(idx+1) for idx,row in dfURIS.iterrows()]
        
        # Save in log
        #dfURIS.to_csv(self.logs+"/uris_with_new_id.csv",index=False)


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

    def generate_new_uri_ComplexSubject(self):

        componentList_ID = []
        data = []
        for s,p,o in self.graphNew.triples((None,None,ns_madsrdf.ComplexSubject)):
            for ss,pp,oo in self.graphNew.triples((s,ns_madsrdf.componentList,None)):
                # Get values data in a Blank Node
                l = list(
                    evalPath(
                        self.graphNew,
                        (oo,
                         ns_rdf.rest / ns_rdf.first,
                         None)
                    )
                )
                c = Collection(self.graphNew,oo)
                [data.append([s,l.split('/')[-1]]) for l in c]                
            
        dfComplex = pd.DataFrame(data=data, columns = ['uri','componentList'])
        dfProcess = dfComplex.groupby(['uri'])['componentList'].apply('_'.join).reset_index()
        dfProcess.sort_values(by='uri',inplace=True)
        dfProcess.reset_index(drop=True, inplace=True)

        CLS = pd.Series(dfProcess['componentList'].to_list()).drop_duplicates().to_list()
        l = []
        for cl in CLS:
            dfF = dfProcess[dfProcess['componentList'] == cl]
            if len(dfF) == 1:
                l.append(dfF)
            else:
                dfUri = dfF.sort_values(by='uri') #.sort_values(by='uri')
                tmp = []
                nSeq = 1
                for idx,row in dfUri.iterrows():
                    uri = row['uri']
                    idseq = str(nSeq)+'_'+row['componentList']
                    nSeq += 1
                    tmp.append([uri,idseq])
                dfSe = pd.DataFrame(data=tmp,columns=['uri','componentList'])
                l.append(dfSe)
        dfGenerator = pd.concat(l)

        # Update URI
        for idx,row in dfGenerator.iterrows():
            subject = URIRef(row['uri'])
            newIdSeq = row['componentList']
            newURI  = URIRef(ns_jurivoc+newIdSeq)
            
            for s,p,o in self.graphNew.triples((subject,None,None)):                            
                self.graphNew.add((newURI,p,o))
                for ss,pp,oo in self.graphNew.triples((None,None,subject)):
                    self.graphNew.add((ss,pp,newURI))
                self.graphNew.remove((None,None,subject))
            self.graphNew.remove((subject,None,None))
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
    
    def get_prefLabel(self, gProcess) -> pd.DataFrame:

        list_PrefLabel = []
        for s,p,o in gProcess.triples((None,None,ns_skos.Concept)):            
            
            listOfPrefLabel = list(evalPath(gProcess,
                                    (s,ns_skos.prefLabel,None)
                                    ))
            [list_PrefLabel.append([pl[0],pl[1]+self.get_lang(pl)]) for pl in listOfPrefLabel]

        dfPref = pd.DataFrame(data=list_PrefLabel, columns=['uri','prefLabel'])
        return dfPref
    
    def get_authoritativeLabel(self,gProcess) -> pd.DataFrame:

        list_Label = []
        for s,p,o in gProcess.triples((None,None,ns_madsrdf.ComplexSubject)):            
            
            list_ALabel = list(evalPath(gProcess,
                                    (s,ns_madsrdf.authoritativeLabel,None)
                                    ))
            [list_Label.append([pl[0],pl[1]+self.get_lang(pl)]) for pl in list_ALabel]

        dfALabel = pd.DataFrame(data=list_Label, columns=['uri','authoritativeLabel'])
        return dfALabel
    
    def update_graph_concept(self,uri,uriOld):

        for s,p,o in self.graphNew.triples((uri,None,None)):
            self.graphNew.add((uriOld,p,o))
            self.graphNew.set((uriOld,ns_dct.identifier,Literal(uriOld.split('/')[-1])))
        self.graphNew.remove((uri,None,None))

        for sObj,pObj,oObj in self.graphNew.triples((None,None,uri)):
            self.graphNew.add((sObj,pObj,uriOld))
        self.graphNew.remove((None,None,uri))
        
        return True        

    def update_graph_ComplexSubject(self,uri,uriOld):

        for s,p,o in self.graphNew.triples((uri,None,None)):
            self.graphNew.add((uriOld,p,o))
        self.graphNew.remove((uri,None,None))

        for sObj,pObj,oObj in self.graphNew.triples((None,None,uri)):
            self.graphNew.add((sObj,pObj,uriOld))
        self.graphNew.remove((None,None,uri))

        return True

    def add_new_concept_graph(self,subject):

        # Update Subject
        id = pd.Series(self.IdSeq).max()
        nMAxSequence = int(id) + 1
        uri = URIRef(ns_jurivoc+str(nMAxSequence))

        for s,p,o in self.graphNew.triples((subject,None,None)):
            self.graphNew.add((uri,p,o))
            self.graphNew.set((uri,ns_dct.identifier,Literal(str(nMAxSequence))))
        self.graphNew.remove((subject,None,None))

        for s,p,o in self.graphNew.triples((None,None,subject)):
            self.graphNew.add((s,p,uri))
        self.graphNew.remove((None,None,subject))

        self.IdSeq.append(nMAxSequence)
        print('{} uri did not match any prefLabel. It is considered like a new Concept with ID {}'.format(subject,str(nMAxSequence)))

        return True

    def add_new_ComplexSubject_graph(self,subject):

        # Update Subject
        csId = pd.Series(self.ComplexSubjectID).max()
        getId = int(csId.split('_')[0]) + 1
        newUri = URIRef(ns_madsrdf+str(getId))
        for s,p,o in self.graphNew.triples((subject,None,None)):
            self.graphNew.add((newUri,p,o))
        self.graphNew.remove((subject,None,None))

        for sObj,pObj,oObj in self.graphNew.triples((None,None,subject)):
            self.graphNew.add((sObj,pObj,newUri))
        self.graphNew.remove((None,None,subject))

        return True

    def process_graph_concept(self,dfNew:pd.DataFrame,dfOld:pd.DataFrame):

        dfMerge = pd.merge(dfNew,dfOld,how='left',on=['prefLabel'])
        dfData = dfMerge.rename({'uri_x': 'uri', 'uri_y': 'uri_old'}, axis='columns')
        dfData.to_csv(os.path.join(self.logs,'Merge_GraphNew_OldGraph.csv'),sep='|',index=False)

        titlesKey = pd.Series(dfData['uri'].to_list()).drop_duplicates().to_list()
        for title in titlesKey:
            # Filter for title
            dfW = dfData[dfData['uri'] == title]

            nUri = len(dfW[~dfW['uri'].isna()])
            nOldUri = len(dfW[~dfW['uri_old'].isna()])

            if nUri == nOldUri:
                # Match all prefLabel
                uriOld = pd.Series(dfW['uri_old'].to_list()).drop_duplicates().to_list()
                if len(uriOld) == 1:
                    newURI = URIRef(str(uriOld[0]))
                    self.update_graph_concept(URIRef(title),newURI)
            else: 
                # If new uri not exis in the current graph                
                if nOldUri == 0:
                    # If uri not exist in Graph, generate new Concept
                    if (URIRef(title),None,None) not in self.graphCurrent:
                        # Add new Concept in the graph
                        self.add_new_concept_graph(title)
                else:
                    uriOldMatch = dfW[~dfW['uri_old'].isna()]['uri_old'].to_list()
                    uriOldNotMatch = len(dfW) - len(uriOldMatch)
                    l_PrefLabel = dfW[dfW['uri_old'].isna()]['prefLabel'].to_list()
                    str_PrefLabel = ','.join(l_PrefLabel)
                    
                    print('Warning: The {} uri: ({}) {} prefLabels not match.'.format(title,uriOldNotMatch,str_PrefLabel))

                    # if only match with prefLabel, generate update in the graph
                    uriOld = pd.Series(uriOldMatch).drop_duplicates().to_list()
                    if len(uriOld) == 1:
                        newURI = URIRef(str(uriOld[0]))
                        self.update_graph_concept(URIRef(title),newURI)
        return True
    
    def process_graph_ComplexSubject(self,dfComplexSubjectNew:pd.DataFrame,dfComplexSubjectOld:pd.DataFrame):

        dfMerge = pd.merge(dfComplexSubjectNew,dfComplexSubjectOld,how='left',on=['authoritativeLabel'])
        dfData = dfMerge.rename({'uri_x': 'uri', 'uri_y': 'uri_old'}, axis='columns')
        dfData.to_csv(os.path.join(self.logs,'Merge_GraphNew_authoritativeLabel.csv'),sep='|',index=False)

        titlesKey = pd.Series(dfData['uri'].to_list()).drop_duplicates().to_list()
        for title in titlesKey:
            # Filter for title
            dfW = dfData[dfData['uri'] == title]
            nUri = len(dfW[~dfW['uri'].isna()])
            nOldUri = len(dfW[~dfW['uri_old'].isna()])

            if nUri == nOldUri:
                uriOld = pd.Series(dfW['uri_old'].to_list()).drop_duplicates().to_list()
                self.update_graph_ComplexSubject(URIRef(title),URIRef(uriOld[0]))
            else:
                if nOldUri == 0:
                    self.add_new_ComplexSubject_graph(title)                    
        return True

    def compare_graph_get_uri(self) -> Graph:
        
        # Get Data value URI, LABELS
        dfgNew = self.get_prefLabel(self.graphNew)
        dfgNew.sort_values(by=["uri"], inplace=True)
        
        dfgOld = self.get_prefLabel(self.graphCurrent)
        dfgOld.sort_values(by=["uri"], inplace=True)
        
        # all URI with Concept
        self.process_graph_concept(dfgNew,dfgOld)
        
        # all URI with ComplexSubject
        dfComplexSubjectNew = self.get_authoritativeLabel(self.graphNew)
        dfComplexSubjectNew.sort_values(by=["uri"], inplace=True)
        dfComplexSubjectOld = self.get_authoritativeLabel(self.graphCurrent)
        dfComplexSubjectOld.sort_values(by=["uri"], inplace=True)

        if not self.noComplexSubjects:
            self.process_graph_ComplexSubject(dfComplexSubjectNew,dfComplexSubjectOld)

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
            if not self.noComplexSubjects:
                self.generate_new_uri_ComplexSubject()
        return self.graphNew


class convert_graph:

    def __init__(self, dataset : list, outputDir, noComplexSubjects:bool) -> None:
        
        self.dataset = dataset
        dir_data_for_graph = os.path.join(outputDir,'data_for_graph')

        isExiste = os.path.exists(dir_data_for_graph)
        if isExiste == False:
            os .makedirs(dir_data_for_graph)     
            self.logs = dir_data_for_graph       
        else:    
            self.logs = outputDir

        self.jurivocGraph = Graph()

        self.jurivocGraph.bind("jurivoc",ns_jurivoc)
        self.jurivocGraph.bind("madsrdf",ns_madsrdf)
        self.jurivocGraph.bind("skos",ns_skos)
        self.jurivocGraph.bind("owl",ns_owl)
        self.jurivocGraph.bind("owl",ns_owl)

        #
        self.noComplexSubjects = noComplexSubjects

        for s in self.dataset:
            if '_fre' in s[0]:
                dfFR = s[1]
                dfTmp = dfFR[dfFR['block'].isin(['USA','AND'])]
                keyTmp = pd.Series(dfTmp['title'].to_list()).drop_duplicates().to_list()
                keyTmp.append("THÉSAURUS")
                dfConceptTitle = dfFR[~dfFR["title"].isin(keyTmp)]
                self.listOfTitleConcept = pd.Series(dfConceptTitle['title'].to_list()).drop_duplicates().to_list()

    def generate_skos_concept(self, df:pd.DataFrame, titlekey:list,titleWithUSE:list) -> Graph:
        # Create a Graph
        
        print('Generate Skos:Concept')

        gConcepts = Graph()        
        for Title in titlekey:
            # get block for each title
            dfFilter = df[df["title"].isin([Title])]
            # find if block contain USE
            block  = dfFilter["block"].to_list()
            # If bExist is false then generate a skos:Concept
            if 'USE' not in block:
                # Convert title to URI
                title_dq = dataquality_text(Title)
                title_uri = URIRef(ns_jurivoc + title_dq)
                
                # Create skos:Concept Graph
                gConcepts.add((title_uri,ns_rdf.type,ns_skos.Concept))
                gConcepts.add((title_uri,ns_rdf.type,URIRef('https://jurivoc.bger.ch/model/Jurivoc')))

                gConcepts.add((title_uri,ns_skos.inScheme,URIRef('https://jurivoc.bger.ch/vocabulary/jurivoc')))
                
                gConcepts.add((title_uri,ns_skos.prefLabel,Literal(remove_c_title(Title), lang="fr")))
                
                gConcepts.add((title_uri,ns_dct.identifier,Literal(title_dq)))
                
                for index, row in dfFilter.iterrows(): 
                    block = row["block"]
                    title_block = row["title_block"]

                    if block:
                        # Generate Skos:altLabel
                        if block == "UF":
                            gConcepts.add((title_uri,ns_skos.altLabel,Literal(title_block, lang="fr")))
                    
                        # Generate skos:broader and skos:narrower
                        if block == "BT":
                            if "THÉSAURUS" in title_block:
                                if title_uri not in self.listOfTitleConcept:
                                    wlog_block.append(['Concept',"THÉSAURUS",'BT',title_uri])

                                gConcepts.add((title_uri,ns_skos.topConceptOf,URIRef("https://jurivoc.bger.ch/vocabulary/jurivoc")))
                                gConcepts.add((URIRef("https://jurivoc.bger.ch/vocabulary/jurivoc"),ns_skos.hasTopConcept,title_uri))
                            else:
                                if title_block not in titleWithUSE:

                                    uri_block = URIRef(ns_jurivoc + dataquality_text(title_block))
                                    if title_block not in self.listOfTitleConcept:
                                        wlog_block.append(['Concept',title_uri,'BT',uri_block])

                                    gConcepts.add((title_uri,ns_skos.broader,uri_block))
                                    # Inverse to skos:broader
                                    gConcepts.add((uri_block,ns_skos.narrower,title_uri))

                        # Generate skos:scopeNote
                        if block == "SN":
                            gConcepts.add((title_uri,ns_skos.scopeNote,Literal(title_block, lang="fr") ))

                        if block == "SA":
                            if title_block not in titleWithUSE:                                
                                # find the title in Concept
                                uri_block = URIRef(ns_jurivoc + dataquality_text(title_block))
                                if title_block not in self.listOfTitleConcept:
                                    wlog_block.append(['Concept',title_uri,'SA',uri_block])
                                gConcepts.add((title_uri,ns_skos.related,URIRef(ns_jurivoc + dataquality_text(title_block))))
                                gConcepts.add((URIRef(ns_jurivoc + dataquality_text(title_block)),ns_skos.related,title_uri))
            
        self.jurivocGraph += gConcepts
        return True
    
    def generate_Thesaurus(self,df:pd.DataFrame) -> Graph:

        print('Generate THESAURUS')

        # get block for each title
        gConceptScheme = Graph()
        # Convert title to URI        
        title_uri = URIRef("https://jurivoc.bger.ch/vocabulary/jurivoc")
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

        print('Generate madsrdf...')

        gSpecific = Graph()
        log_df = []
        for title in titlekey:
            # Get block
            dfTitle = df[df["title"].isin([title])]

            blocks = pd.Series(dfTitle["title"].to_list()).drop_duplicates().to_list()
            if "USE" not in blocks:
                title_dq = dataquality_text(title)
                title_uri = URIRef(ns_jurivoc+title_dq)

                gSpecific.add((title_uri,ns_rdf.type,URIRef(ns_madsrdf.ComplexSubject)))
                gSpecific.add((title_uri,ns_madsrdf.authoritativeLabel,Literal(title,lang="fr")))

                datacomponentList = []
                for idx, row in dfTitle.iterrows():

                    if row["block"] == "USA":
                        
                        titleBlock = dataquality_text(row["title_block"])
                        uriComponent = URIRef(ns_jurivoc+titleBlock)
                        datacomponentList.append(uriComponent)
                        
                        if row["title_block"] not in self.listOfTitleConcept:
                            wlog_block.append(['USA_AND',uriComponent,'USA',title_uri])
                        
                        #
                        gSpecific.add((uriComponent,ns_rdfs.seeAlso,title_uri))
                    
                    if row["block"] == "AND":
                        
                        titleBlock = dataquality_text(row["title_block"])
                        uriComponent = URIRef(ns_jurivoc+titleBlock)
                        datacomponentList.append(uriComponent)

                        if row["title_block"] not in self.listOfTitleConcept:
                            wlog_block.append(['USA_AND',uriComponent,'AND',title_uri])

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

    def generate_language_graph(self, df:pd.DataFrame, conceptKP : list) -> Graph:

        print("Save in graph # {} rows".format(len(df)))

        gLanguage = Graph()
        terms = []
        for index,row in df.iterrows():
            title = row["title"]
            title_uri = URIRef(ns_jurivoc + dataquality_text(title))
            idLang = row["language"]
            
            title_language = row["title_traduction"]

            if title_language != "THESAURUS":
                if title in conceptKP:
                    gLanguage.add((title_uri,ns_skos.prefLabel,Literal(remove_c_title(title_language), lang=idLang)))
                else:
                    terms.append(title)
        dfNotIdentifier = df[df['title'].isin(terms)]
        dfNotIdentifier.to_csv(os.path.join(self.logs,"terms_in_ger_ita_not_found_in_fra.csv"),sep="|",index=False)
        self.jurivocGraph += gLanguage
        return True

    def generate_graph_ger_ita(self,df:pd.DataFrame, nameFile, listConcepts:list) -> Graph:

        # Dataset Languages
        dftranslate = pd.DataFrame()
        for l in self.dataset:
            if "dbLanguage" in l[0]:
                dftranslate = l[1]
        
        dfProcess = df[df['level'] != 1]
        
        keyLanguage = ""
        if 'jurivoc_ger' in nameFile:
            keyLanguage = 'de'
        
        if 'jurivoc_ita' in nameFile:
            keyLanguage = 'it'

        dfLangTranslate = dftranslate[dftranslate['language'] == keyLanguage]
        
        dfMerge = pd.merge(left=dfProcess, right=dfLangTranslate, how='left', left_on='title', right_on='title_traduction')
        dfMerge.columns = ['level','title','block','title_block','title_translate','language','title_language']
        
        dfDB = dfMerge[dfMerge['language'].isin([keyLanguage])]
        dfNotinDB = dfMerge[~dfMerge['language'].isin([keyLanguage])]
        
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
                title_uri = URIRef(ns_jurivoc + dataquality_text(Title))
                title_lang = dfFilter["title"].unique()[0]
                idLang = dfFilter["language"].unique()[0]

                if (Title == "THESAURUS") or (Title == "THÉSAURUS"):
                    gLanguage.add((URIRef("https://jurivoc.bger.ch/vocabulary/jurivoc"),ns_skos.prefLabel,Literal(str(title_lang), lang=idLang)))                    
                else:
                    gLanguage.add((title_uri,ns_skos.prefLabel,Literal(remove_c_title(str(title_lang)), lang=idLang)))
                    for idx, row in dfFilter.iterrows():
                        if row["block"] == "UF":
                            titleBlock = row["title_block"]
                            gLanguage.add((title_uri,ns_skos.altLabel,Literal(str(titleBlock),lang=idLang)))
                            
                        if row["block"] == "SN":
                            titleSN = row["title_block"]
                            gLanguage.add((title_uri,ns_skos.scopeNote,Literal(str(titleSN),lang=idLang) ))
        
        self.jurivocGraph += gLanguage
        return True
    
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
                self.generate_language_graph(df, self.listOfTitleConcept)
            else:                
                if '_fre' in nameFile:

                    # dataframe with USE
                    dfUSETmp = df[df['block'] == 'USE']
                    titleWithUSE = pd.Series(dfUSETmp['title'].to_list()).drop_duplicates().to_list()

                    # USA and AND block specific Data
                    dfTmp = df[df['block'].isin(['USA','AND'])]
                    keyTmp = pd.Series(dfTmp['title'].to_list()).drop_duplicates().to_list()
                    dfTmpFilter = df[df['title'].isin(keyTmp)]
                    dfSpecific = dfTmpFilter[dfTmpFilter['level'] != 1]
                    
                    #logging.info("Graph of data: {} # rows {}".format(nameFile, len(df)))
                    # =================== Graph THÉSAURUS
                    dfTHESAURUS = df[df["title"] == "THÉSAURUS"]
                    dfTHESAURUS.to_csv(os.path.join(self.logs,"thesaurus_graph.csv"),sep="|",index=False)
                    self.generate_Thesaurus(dfTHESAURUS) 
                    
                    # =================== Graph Skos:Concept
                    dfConcept = df[df["title"].isin(self.listOfTitleConcept)]                 
                    dfConcept.to_csv(os.path.join(self.logs,"concepts_graph.csv"),sep="|",index=False)
                    self.generate_skos_concept(dfConcept,self.listOfTitleConcept, titleWithUSE)

                    # =================== Graph Specific blocks
                    #logging.info("Graph specific USA and AND block")
                    if not self.noComplexSubjects:
                        dfSpecific.to_csv(os.path.join(self.logs,"usa_and_graph.csv"),sep="|",index=False)
                        titleUSAAND = pd.Series(dfSpecific["title"].to_list()).drop_duplicates().to_list()
                        self.generate_madsrdf(dfSpecific,titleUSAAND)
                    
                if ('jurivoc_ger' in nameFile) or ('jurivoc_ita' in nameFile):
                    #logging.info("Generate - Graph of data: {}".format(nameFile))

                    dfTmpLanguage = df[df['block'].isin(['UF','SN'])]
                    titles = pd.Series(dfTmpLanguage['title'].to_list()).drop_duplicates().to_list()
                    dfFilter = df[df['title'].isin(titles)]
                    dfProcess = dfFilter[dfFilter['level'] != 1]

                    filecsv = nameFile+'_graph.csv'
                    dfProcess.to_csv(os.path.join(self.logs,filecsv),sep="|",index=False)
                    print('Generate Graph: {}'.format(nameFile))

                    self.generate_graph_ger_ita(dfProcess,nameFile, self.listOfTitleConcept)
        
        if len(wlog_block) > 0:
            dfLogblock = pd.DataFrame(data = wlog_block,columns=['process','uri_not_found','block','uri'])
            dfLogblock.to_csv(os.path.join(self.logs,"uris_not_found_in_concept.csv"),sep='|',index=False)

        return self.jurivocGraph