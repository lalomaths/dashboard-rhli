import streamlit as st
import pandas as pd
from datetime import datetime
import io
import plotly.express as px

# --- Configuração da Página ---
st.set_page_config(
    page_title="Dashboard de Afastamentos Médicos",
    page_icon=" ",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS Customizado para Visual Corporativo ---
st.markdown("""
<style>
    /* Cores corporativas */
    :root {
        --primary: #1e3a5f;
        --secondary: #2c3e50;
        --accent: #0b5e7c;
        --background: #f8fafc;
        --text: #1e293b;
        --border: #e2e8f0;
    }

    /* Métricas */
    div[data-testid="metric-container"] {
        background: white;
        border: 1px solid var(--border);
        border-radius: 8px;
        padding: 16px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }

    div[data-testid="metric-container"] > div {
        color: var(--text);
    }

    div[data-testid="metric-container"] label {
        color: #64748b !important;
        font-size: 0.9rem !important;
        font-weight: 500 !important;
    }

    div[data-testid="metric-container"] div[data-testid="metric-value"] {
        color: var(--primary) !important;
        font-size: 2rem !important;
        font-weight: 600 !important;
    }

    /* Títulos das seções */
    .section-title {
        color: var(--primary);
        font-size: 1.25rem;
        font-weight: 600;
        margin: 1.5rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid var(--border);
    }

    /* DataFrame */
    .stDataFrame {
        border: 1px solid var(--border);
        border-radius: 8px;
        overflow: hidden;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: white;
        border-right: 1px solid var(--border);
    }

    section[data-testid="stSidebar"] .stButton button {
        background: var(--primary);
        color: white;
        border: none;
        border-radius: 6px;
        padding: 0.5rem 1rem;
        font-weight: 500;
        width: 100%;
    }

    section[data-testid="stSidebar"] .stButton button:hover {
        background: var(--secondary);
    }

    /* Headers */
    h1 {
        color: var(--primary) !important;
        font-size: 2rem !important;
        font-weight: 600 !important;
    }

    h2 {
        color: var(--secondary) !important;
        font-size: 1.5rem !important;
        font-weight: 500 !important;
    }

    /* Expander */
    .streamlit-expanderHeader {
        background: white;
        border: 1px solid var(--border);
        border-radius: 8px;
        color: var(--primary);
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

# --- Dicionário de Nomes de CID (igual ao seu) ---
CID_NOMES = {
    # A00–B99 Doenças infecciosas e parasitárias
    'A00':'Cólera','A01':'Febres tifóide/paratifóide','A02':'Outras salmoneloses',
    'A08':'Infecções intestinais virais','A09':'Diarreia e gastroenterite',
    'A15':'Tuberculose respiratória','A16':'Tuberculose respiratória s/ confirmação',
    'A36':'Difteria','A37':'Coqueluche','A38':'Escarlatina',
    'A39':'Infecção meningocócica','A40':'Septicemia estreptocócica',
    'A41':'Outras septicemias','A49':'Infecção bacteriana NE',
    'A50':'Sífilis congênita','A51':'Sífilis precoce','A53':'Sífilis NE',
    'A54':'Infecção gonocócica','A56':'Outras DST por clamídias',
    'A60':'Infecção anorretal por herpesvírus','A63':'Outras doenças venéreas',
    'A70':'Infecção por Chlamydia psittaci','A74':'Outras doenças por clamídias',
    'A80':'Poliomielite aguda','A82':'Raiva','A83':'Encefalite por arbovírus',
    'A84':'Encefalite viral transmitida por carrapatos',
    'A85':'Outras encefalites virais','A86':'Encefalite viral NE',
    'A87':'Meningite viral','A88':'Outras infecções virais do SNC',
    'A90':'Dengue clássica','A91':'Febre hemorrágica do dengue',
    'A92':'Outras febres virais transmitidas por mosquitos',
    'A95':'Febre amarela','A96':'Febre hemorrágica por arenavírus',
    'A98':'Outras febres hemorrágicas virais','A99':'Febre hemorrágica viral NE',
    'B00':'Infecções por herpesvírus','B01':'Varicela','B02':'Herpes zóster',
    'B05':'Sarampo','B06':'Rubéola','B07':'Verrugas virais',
    'B08':'Outras infecções virais com lesões cutâneas',
    'B09':'Infecção viral NE c/ lesões cutâneas','B15':'Hepatite A aguda',
    'B16':'Hepatite B aguda','B17':'Outras hepatites virais agudas',
    'B18':'Hepatite viral crônica','B19':'Hepatite viral NE',
    'B20':'Doença pelo HIV (AIDS)','B24':'Doença pelo HIV NE',
    'B26':'Caxumba','B27':'Mononucleose infecciosa',
    'B34':'Infecção viral de localização NE',
    'B35':'Dermatofitose','B36':'Outras micoses superficiais',
    'B37':'Candidíase','B49':'Micose NE',
    'B50':'Malária por P. falciparum','B54':'Malária NE',
    'B65':'Esquistossomose','B69':'Cisticercose','B76':'Ancilostomíase',
    'B82':'Parasitose intestinal NE','B86':'Escabiose','B99':'Outras doenças infecciosas',
    # C00–D49 Neoplasias
    'C00':'Neoplasia maligna do lábio','C16':'Neo. maligna do estômago',
    'C18':'Neo. maligna do cólon','C20':'Neo. maligna do reto',
    'C22':'Neo. maligna do fígado',
    'C24':'Neo. maligna de outras partes', 'C25':'Neo. maligna do pâncreas',
    'C33':'Neo. maligna da traqueia','C34':'Neo. maligna do brônquio/pulmão',
    'C43':'Melanoma maligno da pele','C44':'Outras neo. malignas da pele',
    'C50':'Neo. maligna da mama','C53':'Neo. maligna do colo do útero',
    'C54':'Neo. maligna do corpo do útero','C56':'Neo. maligna do ovário',
    'C61':'Neo. maligna da próstata','C67':'Neo. maligna da bexiga',
    'C71':'Neo. maligna do encéfalo','C73':'Neo. maligna da tireoide',
    'C79':'Neo. maligna secundária','C80':'Neo. maligna sem especificação',
    'C81':'Doença de Hodgkin','C83':'Linfoma não-Hodgkin difuso',
    'C90':'Mieloma múltiplo','C91':'Leucemia linfoide','C92':'Leucemia mieloide',
    'D25':'Leiomioma do útero','D50':'Anemia por deficiência de ferro',
    # E00–E89 Doenças endócrinas e metabólicas
    'E03':'Hipotireoidismo NE','E04':'Bócio não tóxico','E05':'Tireotoxicose',
    'E06':'Tireoidite','E07':'Outras doenças da tireoide',
    'E10':'Diabetes mellitus tipo 1','E11':'Diabetes mellitus tipo 2',
    'E13':'Outras formas de diabetes mellitus','E14':'Diabetes mellitus NE',
    'E16':'Outros transtornos da secreção pancreática',
    'E20':'Hipoparatireoidismo','E21':'Hiperparatireoidismo',
    'E22':'Hiperfunção da hipófise','E23':'Hipofunção da hipófise',
    'E27':'Outros transtornos da suprarrenal',
    'E28':'Disfunção ovariana','E29':'Disfunção testicular',
    'E34':'Outros transtornos endócrinos','E46':'Desnutrição proteico-calórica NE',
    'E55':'Deficiência de vitamina D','E58':'Deficiência de cálcio',
    'E61':'Deficiência de outros elementos nutricionais',
    'E63':'Outras deficiências nutricionais','E66':'Obesidade',
    'E72':'Outros transtornos do metabolismo de aminoácidos',
    'E78':'Distúrbios do metabolismo de lipoproteínas','E79':'Gota',
    'E83':'Outros transtornos do metabolismo mineral',
    'E86':'Depleção de volume','E87':'Outros transtornos hidroeletrolíticos',
    # F00–F99 Transtornos mentais
    'F00':'Demência na doença de Alzheimer','F01':'Demência vascular',
    'F02':'Demência em outras doenças','F03':'Demência NE',
    'F04':'Síndrome amnéstica orgânica','F05':'Delirium NE',
    'F06':'Outros transtornos mentais orgânicos',
    'F07':'Transtornos de personalidade e comportamento orgânicos',
    'F09':'Transtorno mental orgânico NE',
    'F10':'Transtornos mentais por álcool','F11':'Transtornos por opioides',
    'F12':'Transtornos por canabinoides','F13':'Transtornos por sedativos',
    'F14':'Transtornos por cocaína','F15':'Transtornos por estimulantes',
    'F17':'Transtornos por tabaco','F19':'Transtornos por múltiplas drogas',
    'F20':'Esquizofrenia','F25':'Transtorno esquizoafetivo',
    'F29':'Psicose não-orgânica NE',
    'F30':'Episódio maníaco','F31':'Transtorno afetivo bipolar',
    'F32':'Episódios depressivos','F33':'Transtorno depressivo recorrente',
    'F34':'Transtornos do humor persistentes',
    'F38':'Outros transtornos do humor','F39':'Transtorno do humor NE',
    'F40':'Transtornos fóbico-ansiosos','F41':'Outros transtornos ansiosos',
    'F42':'Transtorno obsessivo-compulsivo','F43':'Reação ao estresse grave',
    'F44':'Transtornos dissociativos','F45':'Transtornos somatoformes',
    'F48':'Outros transtornos neuróticos',
    'F50':'Transtornos alimentares','F51':'Transtornos do sono não-orgânicos',
    'F52':'Disfunção sexual','F54':'Fatores psicológicos em doenças físicas',
    'F60':'Transtornos específicos de personalidade',
    'F63':'Transtornos dos hábitos e dos impulsos',
    'F70':'Retardo mental leve','F71':'Retardo mental moderado',
    'F84':'Transtornos globais do desenvolvimento',
    'F90':'Transtornos hipercinéticos','F91':'Transtornos de conduta',
    'F98':'Outros transtornos emocionais na infância','F99':'Transtorno mental NE',
    # G00–G99 Doenças do sistema nervoso
    'G00':'Meningite bacteriana','G03':'Meningite NE',
    'G04':'Encefalite e encefalomielite','G06':'Abscesso intracraniano',
    'G20':'Doença de Parkinson','G30':'Doença de Alzheimer',
    'G35':'Esclerose múltipla','G40':'Epilepsia','G41':'Estado de mal epiléptico',
    'G43':'Enxaqueca','G44':'Outras síndromes de algias cefálicas',
    'G45':'Ataques isquêmicos transitórios','G47':'Distúrbios do sono',
    'G50':'Transtornos do nervo trigêmeo','G51':'Transtornos do nervo facial',
    'G54':'Transtornos das raízes e plexos nervosos',
    'G55':'Compressão de raízes nervosas','G56':'Mononeuropatias do membro superior',
    'G57':'Mononeuropatias do membro inferior','G58':'Outras mononeuropatias',
    'G61':'Polineuropatia inflamatória','G62':'Outras polineuropatias',
    'G80':'Paralisia cerebral','G89':'Dor NE','G99':'Outros transtornos do SN',
    # H00–H59 Olho
    'H00':'Hordéolo e calázio','H01':'Outras inflamações da pálpebra',
    'H10':'Conjuntivite','H11':'Outros transtornos da conjuntiva',
    'H16':'Ceratite','H18':'Outros transtornos da córnea',
    'H25':'Catarata senil','H26':'Outras cataratas','H27':'Outros transtornos do cristalino',
    'H35':'Outros transtornos da retina','H40':'Glaucoma',
    'H52':'Transtornos da refração e acomodação','H53':'Transtornos visuais',
    'H54':'Cegueira e visão subnormal','H57':'Outros transtornos do olho',
    # H60–H95 Ouvido
    'H60':'Otite externa','H61':'Outros transtornos do ouvido externo',
    'H65':'Otite média não supurativa','H66':'Otite média supurativa',
    'H70':'Mastoidite','H72':'Perfuração da membrana timpânica',
    'H81':'Transtornos da função vestibular','H83':'Outros transtornos do ouvido interno',
    'H90':'Perda de audição por condução','H91':'Outras perdas de audição',
    'H92':'Otalgia e otorreia','H93':'Outros transtornos do ouvido',
    # I00–I99 Doenças do aparelho circulatório
    'I00':'Febre reumática s/ comprometimento cardíaco',
    'I05':'Doenças reumáticas da valva mitral',
    'I10':'Hipertensão essencial','I11':'Doença cardíaca hipertensiva',
    'I12':'Doença renal hipertensiva','I13':'Doenças hipertensivas combinadas',
    'I15':'Hipertensão secundária',
    'I20':'Angina pectoris','I21':'Infarto agudo do miocárdio',
    'I22':'Infarto do miocárdio subsequente','I24':'Outras doenças isquêmicas agudas',
    'I25':'Doença isquêmica crônica do coração',
    'I26':'Embolia pulmonar','I27':'Outras doenças cardíacas pulmonares',
    'I30':'Pericardite aguda','I33':'Endocardite aguda e subaguda',
    'I34':'Transtornos não reumáticos da valva mitral',
    'I35':'Transtornos não reumáticos da valva aórtica',
    'I42':'Cardiomiopatia','I44':'Bloqueio atrioventricular',
    'I45':'Outros transtornos da condução','I47':'Taquicardia paroxística',
    'I48':'Fibrilação e flutter atrial','I49':'Outras arritmias cardíacas',
    'I50':'Insuficiência cardíaca','I51':'Complicações mal definidas do coração',
    'I60':'Hemorragia subaracnóidea','I61':'Hemorragia intracerebral',
    'I63':'Infarto cerebral','I64':'AVC NE','I67':'Outras doenças cerebrovasculares',
    'I69':'Sequelas de doenças cerebrovasculares',
    'I70':'Aterosclerose','I73':'Outras doenças vasculares periféricas',
    'I74':'Embolia e trombose arteriais','I80':'Flebite e tromboflebite',
    'I83':'Varizes dos membros inferiores','I84':'Hemorroidas',
    'I87':'Outros transtornos das veias','I89':'Outros transtornos dos vasos linfáticos',
    'I95':'Hipotensão','I99':'Outros transtornos do aparelho circulatório',
    # J00–J99 Doenças do aparelho respiratório
    'J00':'Rinofaringite aguda (resfriado comum)','J01':'Sinusite aguda',
    'J02':'Faringite aguda','J03':'Amigdalite aguda','J04':'Laringite e traqueíte agudas',
    'J05':'Laringotraqueíte aguda obstrutiva e epiglotite',
    'J06':'Infecções agudas das vias aéreas superiores NE',
    'J09':'Influenza por vírus identificado','J10':'Influenza por outro vírus',
    'J11':'Influenza - vírus não identificado',
    'J12':'Pneumonia viral','J13':'Pneumonia pneumocócica','J14':'Pneumonia por H. influenzae',
    'J15':'Pneumonia bacteriana NE','J18':'Pneumonia NE',
    'J20':'Bronquite aguda','J21':'Bronquiolite aguda','J22':'Infecção aguda das VAS NE',
    'J30':'Rinite alérgica e vasomotora','J31':'Rinite/rinofaringite/faringite crônicas',
    'J32':'Sinusite crônica','J33':'Pólipo nasal','J34':'Outros transtornos do nariz',
    'J35':'Doenças crônicas das amígdalas e adenoides','J36':'Abscesso periamigdaliano',
    'J37':'Laringite e laringotraqueíte crônicas','J38':'Doenças das cordas vocais e laringe',
    'J39':'Outras doenças das vias aéreas superiores',
    'J40':'Bronquite NE','J41':'Bronquite crônica simples e mucopurulenta',
    'J42':'Bronquite crônica NE','J43':'Enfisema','J44':'DPOC',
    'J45':'Asma','J46':'Estado de mal asmático','J47':'Bronquiectasia',
    'J60':'Pneumoconiose dos mineiros','J63':'Pneumoconiose por outros pós inorgânicos',
    'J68':'Afecção respiratória por substâncias químicas',
    'J70':'Afecções respiratórias por outros agentes externos',
    'J80':'Síndrome do desconforto respiratório do adulto',
    'J84':'Outras doenças pulmonares intersticiais','J85':'Abscesso pulmonar',
    'J90':'Derrame pleural','J93':'Pneumotórax','J96':'Insuficiência respiratória',
    'J98':'Outros transtornos respiratórios','J99':'Transtornos respiratórios NE',
    # K00–K93 Doenças do aparelho digestivo
    'K00':'Transtornos do desenvolvimento dos dentes',
    'K02':'Cárie dentária','K04':'Doenças da polpa e dos tecidos periapicais',
    'K05':'Gengivite e doença periodontal','K08':'Outros transtornos dos dentes',
    'K10':'Outras doenças dos maxilares','K12':'Estomatite e afecções relacionadas',
    'K13':'Outras doenças dos lábios e da mucosa oral',
    'K21':'Doença de refluxo gastroesofágico','K22':'Outras doenças do esôfago',
    'K25':'Úlcera gástrica','K26':'Úlcera duodenal','K27':'Úlcera péptica',
    'K29':'Gastrite e duodenite','K30':'Dispepsia funcional',
    'K31':'Outras doenças do estômago e duodeno',
    'K35':'Apendicite aguda','K37':'Apendicite NE','K38':'Outras doenças do apêndice',
    'K40':'Hérnia inguinal','K41':'Hérnia femoral','K42':'Hérnia umbilical',
    'K43':'Hérnia ventral','K44':'Hérnia diafragmática','K46':'Hérnia abdominal NE',
    'K50':'Doença de Crohn','K51':'Colite ulcerativa','K52':'Outras gastroenterocolites',
    'K57':'Doença diverticular do intestino','K58':'Síndrome do intestino irritável',
    'K59':'Outros transtornos funcionais do intestino','K60':'Fissura e fístula anal',
    'K61':'Abscesso anal e retal','K62':'Outras doenças do ânus e reto',
    'K63':'Outras doenças do intestino',
    'K70':'Doença alcoólica do fígado','K72':'Insuficiência hepática',
    'K73':'Hepatite crônica NE','K74':'Fibrose e cirrose hepáticas',
    'K75':'Outras doenças inflamatórias do fígado','K76':'Outras doenças do fígado',
    'K80':'Colelitíase','K81':'Colecistite','K82':'Outras doenças da vesícula biliar',
    'K83':'Outras doenças das vias biliares','K85':'Pancreatite aguda',
    'K86':'Outras doenças do pâncreas','K92':'Outras doenças do aparelho digestivo',
    # L00–L99 Doenças da pele
    'L01':'Impetigo','L02':'Abscesso cutâneo, furúnculo e carbúnculo',
    'L03':'Celulite','L04':'Linfadenite aguda','L05':'Cisto pilonidal',
    'L08':'Outras infecções locais da pele','L10':'Pênfigo',
    'L20':'Dermatite atópica','L21':'Dermatite seborreica','L22':'Dermatite das fraldas',
    'L23':'Dermatite alérgica de contato','L24':'Dermatite de contato por irritantes',
    'L25':'Dermatite de contato NE','L26':'Dermatite esfoliativa',
    'L27':'Dermatite devida a substâncias ingeridas',
    'L28':'Líquen simples crônico e prurigo','L29':'Prurido',
    'L30':'Outras dermatites','L40':'Psoríase','L41':'Parasoríase',
    'L43':'Líquen plano','L50':'Urticária','L51':'Eritema multiforme',
    'L53':'Outras afecções eritematosas','L55':'Queimadura solar',
    'L57':'Alterações da pele devidas a radiação crônica',
    'L60':'Transtornos das unhas','L63':'Alopecia areata',
    'L70':'Acne','L71':'Rosácea','L72':'Cistos foliculares da pele',
    'L73':'Outros transtornos foliculares','L80':'Vitiligo',
    'L84':'Calosidades','L89':'Úlcera de decúbito','L97':'Úlcera do membro inferior',
    'L98':'Outras afecções da pele NE',
    # M00–M99 Doenças do sistema osteomuscular
    'M00':'Artrite piogênica','M05':'Artrite reumatoide soropositiva',
    'M06':'Outras artrites reumatoides','M07':'Artropatias psoriásicas e entéropáticas',
    'M08':'Artrite juvenil','M10':'Gota','M13':'Outras artrites',
    'M15':'Poliartroses','M16':'Coxartrose','M17':'Gonartrose',
    'M19':'Outras artroses','M20':'Deformidades adquiridas dos dedos',
    'M23':'Transtornos internos do joelho','M24':'Outros transtornos articulares específicos',
    'M25':'Outros transtornos articulares NE',
    'M40':'Cifose e lordose','M41':'Escoliose','M43':'Outras dorsopatias deformantes',
    'M45':'Espondilite anquilosante','M47':'Espondilose',
    'M48':'Outras espondilopatias','M50':'Transtornos dos discos cervicais',
    'M51':'Outros transtornos dos discos intervertebrais',
    'M54':'Dorsalgia','M60':'Miosite','M62':'Outros transtornos musculares',
    'M65':'Sinovite e tenossinovite','M67':'Outros transtornos dos tendões',
    'M70':'Transtornos dos tecidos moles relacionados ao uso',
    'M71':'Outras bursopatias','M72':'Transtornos fibroblásticos',
    'M75':'Lesões do ombro','M76':'Entesopatias dos membros inferiores',
    'M77':'Outras entesopatias','M79':'Outros transtornos dos tecidos moles',
    'M80':'Osteoporose com fratura','M81':'Osteoporose s/ fratura',
    'M84':'Transtornos da continuidade dos ossos',
    'M85':'Outros transtornos da densidade e estrutura óssea',
    'M86':'Osteomielite','M87':'Osteonecrose','M89':'Outros transtornos dos ossos',
    'M93':'Outras osteocondroses','M99':'Lesões biomecânicas NE',
    # N00–N99 Doenças do aparelho geniturinário
    'N00':'Síndrome nefrítica aguda','N02':'Hematúria recidivante',
    'N03':'Síndrome nefrítica crônica','N04':'Síndrome nefrótica',
    'N10':'Nefrite tubulointersticial aguda','N11':'Nefrite tubulointersticial crônica',
    'N12':'Nefrite tubulointersticial NE','N13':'Uropatia obstrutiva e por refluxo',
    'N17':'Insuficiência renal aguda','N18':'Doença renal crônica',
    'N19':'Insuficiência renal NE','N20':'Cálculo do rim e do ureter',
    'N21':'Cálculo do trato urinário inferior','N23':'Cólica renal NE',
    'N25':'Transtornos resultantes da função tubular renal',
    'N28':'Outros transtornos do rim e ureter','N30':'Cistite',
    'N34':'Uretrite e síndrome uretral','N35':'Estenose uretral',
    'N36':'Outros transtornos da uretra','N39':'Outros transtornos do trato urinário',
    'N40':'Hiperplasia da próstata','N41':'Doenças inflamatórias da próstata',
    'N42':'Outros transtornos da próstata','N43':'Hidrocele e espermatocele',
    'N44':'Torção do testículo','N45':'Orquite e epididimite',
    'N47':'Prepúcio redundante e fimose','N48':'Outros transtornos do pênis',
    'N60':'Displasia mamária','N61':'Doenças inflamatórias da mama',
    'N63':'Nódulo mamário NE','N64':'Outros transtornos da mama',
    'N70':'Salpingite e ooforite','N71':'Doença inflamatória do útero',
    'N72':'Doença inflamatória do colo do útero',
    'N73':'Outras doenças inflamatórias pélvicas','N75':'Doenças da glândula de Bartholin',
    'N76':'Outras inflamações da vagina e da vulva',
    'N80':'Endometriose','N81':'Prolapso genital feminino',
    'N83':'Transtornos não inflamatórios do ovário',
    'N84':'Pólipo do trato genital feminino',
    'N85':'Outros transtornos não inflamatórios do útero',
    'N87':'Displasia do colo do útero','N89':'Outros transtornos não inflamatórios da vagina',
    'N92':'Menstruação excessiva e frequente','N93':'Outras hemorragias uterinas',
    'N94':'Dor e outros transtornos genitais femininos','N95':'Transtornos da menopausa',
    'N97':'Infertilidade feminina','N99':'Outros transtornos do aparelho geniturinário',
    # O00–O99 Gravidez, parto e puerpério
    'O00':'Gravidez ectópica','O01':'Mola hidatiforme','O02':'Outros produtos anormais da concepção',
    'O03':'Aborto espontâneo','O04':'Aborto por razões médicas',
    'O08':'Complicações de aborto','O10':'Hipertensão pré-existente na gravidez',
    'O11':'Distúrbio hipertensivo superposto',
    'O13':'Hipertensão gestacional','O14':'Pré-eclâmpsia','O15':'Eclâmpsia',
    'O20':'Hemorragia do início da gravidez','O21':'Vômitos excessivos na gravidez',
    'O22':'Complicações venosas na gravidez','O23':'Infecção geniturinária na gravidez',
    'O24':'Diabetes mellitus na gravidez','O26':'Cuidados maternos por outras condições',
    'O28':'Achados anormais no exame pré-natal','O30':'Gestação múltipla',
    'O34':'Cuidados maternos por anormalidade pélvica',
    'O36':'Cuidados maternos por outros problemas fetais',
    'O42':'Ruptura prematura de membranas','O44':'Placenta prévia',
    'O45':'Descolamento prematuro da placenta','O47':'Falso trabalho de parto',
    'O60':'Trabalho de parto prematuro','O62':'Anormalidades das forças do parto',
    'O63':'Trabalho de parto prolongado','O64':'Trabalho de parto obstruído',
    'O68':'Parto complicado por sofrimento fetal',
    'O70':'Laceração perineal durante o parto','O72':'Hemorragia pós-parto',
    'O80':'Parto único espontâneo','O82':'Parto por cesariana',
    'O85':'Sepse puerperal','O86':'Outras infecções puerperais',
    'O87':'Complicações venosas no puerpério','O90':'Complicações do puerpério',
    'O99':'Outras doenças maternas que complicam a gravidez',
    #Q00–R99 Malformações congênitas, deformidades e anomalias cromossômicas
    'Q898':'Outras malformações congênitas especificadas',
    # R00–R99 Sintomas e sinais
    'R00':'Anormalidades do batimento cardíaco','R01':'Sopros e outros sons cardíacos',
    'R04':'Hemorragia das vias respiratórias','R05':'Tosse',
    'R06':'Anormalidades da respiração','R07':'Dor de garganta e no peito',
    'R09':'Outros sintomas do aparelho circulatório e respiratório',
    'R10':'Dor abdominal e pélvica','R11':'Náusea e vômitos','R12':'Pirose',
    'R13':'Disfagia','R14':'Flatulência e afecções relacionadas',
    'R19':'Outros sintomas do aparelho digestivo','R20':'Perturbações da sensibilidade cutânea',
    'R21':'Eritema e outras erupções cutâneas NE',
    'R22':'Tumefação, massa e caroço localizados','R23':'Outras alterações cutâneas',
    'R25':'Movimentos involuntários anormais','R26':'Anormalidades da marcha e da mobilidade',
    'R29':'Outros sintomas do sistema nervoso e músculo-esquelético',
    'R30':'Dor associada à micção','R31':'Hematúria NE','R32':'Incontinência urinária NE',
    'R33':'Retenção urinária','R34':'Anúria e oligúria','R35':'Poliúria',
    'R39':'Outros sintomas do aparelho urinário','R41':'Outros sintomas cognitivos e da consciência',
    'R42':'Tontura e instabilidade','R43':'Perturbações do olfato e do paladar',
    'R44':'Outros sintomas do sistema nervoso','R45':'Sintomas relativos ao estado emocional',
    'R47':'Perturbações da fala','R50':'Febre de causa desconhecida','R51':'Cefaleia',
    'R52':'Dor NE','R53':'Mal-estar e fadiga','R54':'Senilidade',
    'R55':'Síncope e colapso','R56':'Convulsões NE','R57':'Choque NE',
    'R60':'Edema NE','R63':'Sintomas relativos à ingestão de alimentos',
    'R65':'Síndrome da resposta inflamatória sistêmica',
    'R68':'Outros sintomas e sinais gerais','R69':'Causas desconhecidas e não especificadas',
    # S00–T98 Lesões e envenenamentos
    'S00':'Traumatismo superficial da cabeça','S01':'Ferimento da cabeça',
    'S02':'Fratura do crânio e dos ossos da face','S06':'Traumatismo intracraniano',
    'S09':'Outros traumatismos da cabeça','S10':'Traumatismo superficial do pescoço',
    'S12':'Fratura do pescoço','S13':'Luxação do pescoço','S20':'Traumatismo superficial do tórax',
    'S22':'Fratura das costelas e esterno','S29':'Outros traumatismos do tórax',
    'S30':'Traumatismo superficial do abdome','S32':'Fratura da coluna lombar e pelve',
    'S39':'Outros traumatismos do abdome','S40':'Traumatismo superficial do ombro/braço',
    'S42':'Fratura do ombro e do braço','S43':'Luxação do ombro','S46':'Lesão de tendão do ombro',
    'S49':'Outros traumatismos do ombro','S50':'Traumatismo superficial do cotovelo/antebraço',
    'S52':'Fratura do antebraço','S60':'Traumatismo superficial do punho e mão',
    'S62':'Fratura ao nível do punho e da mão','S63':'Luxação do punho e da mão',
    'S70':'Traumatismo superficial do quadril/coxa','S72':'Fratura do fêmur',
    'S80':'Traumatismo superficial da perna','S82':'Fratura da perna',
    'S83':'Luxação e entorse do joelho','S90':'Traumatismo superficial do tornozelo/pé',
    'S92':'Fratura do pé','S93':'Luxação do tornozelo e do pé',
    'T07':'Traumatismos múltiplos NE','T08':'Fratura da coluna NE',
    'T09':'Outros traumatismos da coluna NE','T14':'Traumatismo de região do corpo NE',
    'T78':'Efeitos adversos NE','T79':'Certas complicações precoces dos traumatismos',
    'T91':'Sequelas de traumatismos do pescoço e tronco',
    # Z00–Z99 Fatores que influenciam o estado de saúde
    'Z00':'Exame geral (check-up)','Z01':'Outros exames especiais',
    'Z02':'Exames para fins administrativos',
    'Z03':'Observação médica por suspeita de doenças',
    'Z04':'Exame e observação por outras razões','Z08':'Exame de seguimento',
    'Z09':'Acompanhamento após tratamento NE','Z10':'Exame de saúde de rotina',
    'Z11':'Exame especial de rastreamento','Z12':'Exame especial para neoplasia',
    'Z13':'Exame especial para outras doenças/transtornos',
    'Z20':'Contato com doenças infecciosas','Z21':'Infecção assintomática pelo HIV',
    'Z22':'Portador de doenças infecciosas','Z23':'Necessidade de imunização',
    'Z29':'Outras profilaxias',
    'Z30':'Anticoncepção','Z34':'Supervisão de gravidez normal',
    'Z36':'Rastreamento pré-natal','Z37':'Resultado do parto',
    'Z39':'Cuidados e exames do pós-parto',
    'Z51':'Outros cuidados médicos','Z54':'Convalescença',
    'Z55':'Problemas relacionados à educação e alfabetização',
    'Z56':'Problemas relacionados ao emprego','Z57':'Exposição ocupacional a fatores de risco',
    'Z58':'Problemas relacionados ao ambiente físico',
    'Z59':'Problemas relacionados à habitação e condições econômicas',
    'Z60':'Problemas relacionados ao ambiente social',
    'Z62':'Problemas relacionados à criação dos filhos',
    'Z63':'Outros problemas relacionados ao grupo familiar',
    'Z65':'Problemas relacionados a circunstâncias psicossociais',
    'Z71':'Pessoas em contato com serviços de saúde para orientação',
    'Z73':'Problemas relacionados à organização do modo de vida',
    'Z74':'Problemas relacionados à dependência de cuidador',
    'Z75':'Problemas relacionados a recursos de assistência médica',
    'Z76':'Pessoas em contato com serviços de saúde em outras circunstâncias',
    'Z80':'História familiar de neoplasia maligna',
    'Z82':'História familiar de determinadas incapacidades e doenças',
    'Z85':'História pessoal de neoplasia maligna',
    'Z87':'História pessoal de outras doenças e afecções',
    'Z96':'Presença de outros implantes funcionais',
    'Z98':'Outros estados pós-cirúrgicos','Z99':'Dependência de máquinas e dispositivos',
}

# --- Funções de Utilidade ---
@st.cache_data
def load_data(file_name):
    """Carrega e prepara o DataFrame a partir de um arquivo CSV."""
    try:
        df = pd.read_csv(file_name)
        # Converte a coluna DATA para datetime
        df['DATA'] = pd.to_datetime(df['DATA'], dayfirst=True, errors='coerce')
        # Remove linhas com data inválida
        df.dropna(subset=['DATA'], inplace=True)

        # Cria colunas auxiliares
        df['SEMANA_MES'] = (df['DATA'].dt.day - 1) // 7 + 1
        traducao = {
            'Monday': 'Segunda-feira', 'Tuesday': 'Terca-feira',
            'Wednesday': 'Quarta-feira', 'Thursday': 'Quinta-feira',
            'Friday': 'Sexta-feira', 'Saturday': 'Sabado', 'Sunday': 'Domingo'
        }
        df['DIA_SEMANA'] = df['DATA'].dt.day_name().map(traducao)
        df['TIPO'] = pd.cut(df['DIAS'], bins=[0, 3, 15, 9999], labels=['Curto (1-3d)', 'Medio (4-15d)', 'Longo (15d+)'])
        df['MES_ANO'] = df['DATA'].dt.strftime('%B %Y').str.capitalize()
        return df
    except FileNotFoundError:
        st.error(f"Arquivo {file_name} não encontrado. Certifique-se de que ele está no mesmo diretório do dashboard.")
        return None
    except Exception as e:
        st.error(f"Erro ao carregar {file_name}: {e}")
        return None

def get_cid_nome(codigo, max_len=50):
    """Retorna nome do CID ou o próprio código se não encontrado."""
    if pd.isna(codigo) or not isinstance(codigo, str):
        return str(codigo)
    upper = codigo.strip().upper()
    nome = CID_NOMES.get(upper) or CID_NOMES.get(upper[:3])
    if nome:
        return f"{upper} - {nome[:max_len]}"
    return upper

# --- Mapeamento de Grupos por Letra CID-10 ---
CID_GRUPOS = {
    'A': "Doenças Infecciosas",
    'B': "Doenças Infecciosas",
    'C': "Neoplasias",
    'D': "Doenças do Sangue / Neoplasias",
    'E': "Doenças Endócrinas e Metabólicas",
    'F': "Transtornos Mentais",
    'G': "Doenças do Sistema Nervoso",
    'H': "Olhos e Ouvidos",
    'I': "Doenças Circulatórias",
    'J': "Doenças Respiratórias",
    'K': "Doenças Digestivas",
    'L': "Doenças da Pele",
    'M': "Doenças Osteomusculares",
    'N': "Doenças Geniturinária",
    'O': "Gravidez e Parto",
    'P': "Condições Perinatais",
    'Q': "Malformações Congênitas",
    'R': "Sinais e Sintomas",
    'S': "Lesões e Envenenamentos",
    'T': "Lesões e Envenenamentos",
    'V': "Causas Externas",
    'W': "Causas Externas",
    'X': "Causas Externas",
    'Y': "Causas Externas",
    'Z': "Fatores que Influenciam a Saúde",
    'U': "Emergências Sanitárias",
}

def get_grupo_cid(codigo):
    """Retorna o grupo (afecção) com base na letra inicial do CID."""
    if pd.isna(codigo) or not isinstance(codigo, str) or not codigo.strip():
        return "Não Classificado"
    return CID_GRUPOS.get(codigo.strip().upper()[0], "Não Classificado")


def plot_treemap_capitulos(df):
    """Gera treemap de afastamentos segmentados por grupo de afecção (letra CID-10)."""
    df2 = df.copy()
    df2['GRUPO'] = df2['CID'].apply(get_grupo_cid)

    cap_group = (
        df2.groupby('GRUPO')
        .agg(
            Atestados=('CID', 'count'),
            Total_Dias=('DIAS', 'sum'),
            Media_Dias=('DIAS', 'mean')
        )
        .reset_index()
    )
    cap_group = cap_group[cap_group['Atestados'] > 0].sort_values('Atestados', ascending=False)
    cap_group['Media_Dias'] = cap_group['Media_Dias'].round(1)

    cores = [
        "#1e3a5f","#0b5e7c","#2c7be5","#27a844","#e74c3c",
        "#9b59b6","#f39c12","#16a085","#8e44ad","#2980b9",
        "#c0392b","#27ae60","#d35400","#7f8c8d","#1abc9c",
        "#e67e22","#3498db","#e91e63","#00bcd4","#ff5722",
        "#607d8b","#795548",
    ]

    fig = px.treemap(
        cap_group,
        path=['GRUPO'],
        values='Atestados',
        color='GRUPO',
        color_discrete_sequence=cores,
        custom_data=['Total_Dias', 'Media_Dias', 'Atestados'],
    )

    fig.update_traces(
        texttemplate="<b>%{label}</b><br>%{customdata[2]} atestados<br>%{customdata[0]} dias",
        textfont=dict(size=13, family="Arial", color="white"),
        hovertemplate=(
            "<b>%{label}</b><br>"
            "Atestados: %{customdata[2]}<br>"
            "Total de Dias: %{customdata[0]}<br>"
            "Média de Dias: %{customdata[1]}<br>"
            "<extra></extra>"
        ),
        marker=dict(line=dict(width=2, color='white')),
    )

    fig.update_layout(
        margin=dict(t=10, l=10, r=10, b=10),
        height=520,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        showlegend=False,
    )
    return fig, cap_group

# --- Configuração dos Arquivos ---
ARQUIVOS = {
    "Dezembro 2025": "BASE DE DADOS DEZEMBRO 2025.csv",
    "Janeiro 2026": "BASE DE DADOS JANEIRO 2026.csv",
    "Fevereiro 2026": "BASE DE DADOS FEVEREIRO 2026.csv",
}

# --- Tela de Seleção (Sidebar) ---
st.sidebar.markdown("<h2 style='color: #1e3a5f; margin-bottom: 2rem; text-align: center;'>Dashboard de Afastamentos Médicos</h2>", unsafe_allow_html=True)
st.sidebar.markdown("---")

# Seleção do Mês
mes_selecionado = st.sidebar.selectbox(
    "Selecione o período",
    options=list(ARQUIVOS.keys())
)

# Botão para carregar/navegar
if st.sidebar.button("Carregar dados", type="primary", use_container_width=True):
    st.session_state['mes_selecionado'] = mes_selecionado
    st.session_state['arquivo_selecionado'] = ARQUIVOS[mes_selecionado]
    st.session_state.pop("treemap_grupo", None)
    st.rerun()

st.sidebar.markdown("<br>", unsafe_allow_html=True)

col1, col2, col3 = st.sidebar.columns([1, 2, 1])
with col2:
    st.image("lalo.png", use_container_width=True)
st.sidebar.markdown("""
<div style='text-align: center;'>
    <p stylestyle='color: #64748b; font-size: 0.8rem; margin: 0;'>Da planilha ao dashboard —
coleta, tratamento dos dados e desenvolvimento da aplicação por:</p>
    <p style='color: #1e3a5f; font-weight: 600; margin: 6px 0 2px 0;'>Jorge Eduardo de Araujo Oliveira</p>
    <p style='color: #64748b; font-size: 0.8rem; margin: 0;'>Tecnólogo em Análise e Desenvolvimento de Sistemas</p>
</div>
""", unsafe_allow_html=True)

# --- Tela Principal ---
# Verifica se um mês foi selecionado e carregado
if 'arquivo_selecionado' in st.session_state:
    arquivo = st.session_state['arquivo_selecionado']
    mes_nome = st.session_state['mes_selecionado']

    # Carrega os dados
    df = load_data(arquivo)

    if df is not None and not df.empty:
        # Título da Página
        st.markdown(f"<h1>CAGEPA - RHLI - Dashboard de Afastamentos Médicos</h1>", unsafe_allow_html=True)
        st.markdown(f"<p style='color: #64748b; margin-top: -0.5rem;'>{mes_nome} • {len(df)} registros</p>", unsafe_allow_html=True)
        st.markdown("---")

        # --- Layout com Colunas ---

        # Linha 1: Métricas Gerais em Cards
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("Total Atestados", len(df))
        with col2:
            st.metric("Funcionários", df['MAT'].nunique())
        with col3:
            st.metric("Total Dias", f"{df['DIAS'].sum()} dias")
        with col4:
            st.metric("Média por Atestado", f"{df['DIAS'].mean():.1f} dias")
        with col5:
            st.metric("Maior Afastamento", f"{df['DIAS'].max()} dias")

        st.markdown("---")

        # Linha 2: Gráficos de Distribuição
        col_left, col_right = st.columns(2)

        with col_left:
            st.markdown("<p class='section-title'>Distribuição por Duração</p>", unsafe_allow_html=True)
            tipo_counts = df['TIPO'].value_counts().reset_index()
            tipo_counts.columns = ['Duração', 'Quantidade']
            st.bar_chart(tipo_counts.set_index('Duração'))

        with col_right:
            st.markdown("<p class='section-title'>Atestados por Dia da Semana</p>", unsafe_allow_html=True)
            ordem_dias = ['Segunda-feira', 'Terca-feira', 'Quarta-feira', 'Quinta-feira', 'Sexta-feira', 'Sabado', 'Domingo']
            dia_counts = df['DIA_SEMANA'].value_counts().reindex(ordem_dias).fillna(0).reset_index()
            dia_counts.columns = ['Dia da Semana', 'Quantidade']
            st.bar_chart(dia_counts.set_index('Dia da Semana'))

        st.markdown("---")

        # Linha 3: Tabelas Frequentes
        st.markdown("<p class='section-title'>CIDs Mais Frequentes</p>", unsafe_allow_html=True)
        cid_counts = df['CID'].value_counts().head(10).reset_index()
        cid_counts.columns = ['CID', 'Quantidade']
        # Aplica a formatação aos códigos CID
        cid_counts['CID'] = cid_counts['CID'].apply(get_cid_nome)
        st.dataframe(cid_counts, use_container_width=True, hide_index=True)

        st.markdown("---")

        # Linha 3b: Treemap por Capítulos CID-10
        st.markdown("<p class='section-title'>Afastamentos por Grupo de Afecção (CID-10)</p>", unsafe_allow_html=True)

        fig_treemap, cap_group = plot_treemap_capitulos(df)

        col_treemap, col_btn = st.columns([8, 1])
        with col_treemap:
            st.caption("Clique em um bloco para ver os atestados detalhados.")
        with col_btn:
            if st.button("✖ Limpar", key="limpar_treemap", help="Voltar à visão geral"):
                st.session_state.pop("treemap_grupo", None)
                st.rerun()

        # Captura clique no treemap
        click_event = st.plotly_chart(
            fig_treemap,
            use_container_width=True,
            on_select="rerun",
            key="treemap_click"
        )

        # Atualiza grupo selecionado na session_state
        if click_event and click_event.get("selection") and click_event["selection"].get("points"):
            ponto = click_event["selection"]["points"][0]
            label = ponto.get("label") or ponto.get("id") or ""
            grupos_validos = set(cap_group['GRUPO'].tolist())
            if label in grupos_validos:
                st.session_state["treemap_grupo"] = label
            else:
                # Clicou fora de um grupo válido (raiz/zoom-out) → limpa
                st.session_state.pop("treemap_grupo", None)

        grupo_clicado = st.session_state.get("treemap_grupo")

        if grupo_clicado:
            df_detalhe = df.copy()
            df_detalhe['GRUPO'] = df_detalhe['CID'].apply(get_grupo_cid)
            df_detalhe = df_detalhe[df_detalhe['GRUPO'] == grupo_clicado].copy()
            df_detalhe['CID_NOME'] = df_detalhe['CID'].apply(get_cid_nome)
            # Ordena por data (datetime) antes de formatar para string
            df_detalhe = df_detalhe.sort_values('DATA', ascending=True)
            df_detalhe['DATA'] = df_detalhe['DATA'].dt.strftime('%d/%m/%Y')

            st.markdown(
                f"<p class='section-title'>📋 Detalhamento — {grupo_clicado} "
                f"<span style='font-weight:400;font-size:0.95rem;color:#64748b;'>"
                f"({len(df_detalhe)} atestados · {df_detalhe['DIAS'].sum()} dias)</span></p>",
                unsafe_allow_html=True
            )
            st.dataframe(
                df_detalhe[['CID', 'CID_NOME', 'MAT', 'DATA', 'DIAS']]
                    .rename(columns={
                        'CID_NOME': 'Descrição',
                        'MAT': 'Matrícula',
                        'DATA': 'Data',
                        'DIAS': 'Dias'
                    })
                    .reset_index(drop=True),
                use_container_width=True,
                hide_index=True
            )
        else:
            with st.expander("Ver tabela resumo por grupo de afecção"):
                cap_display = cap_group[['GRUPO', 'Atestados', 'Total_Dias', 'Media_Dias']].copy()
                cap_display.columns = ['Grupo de Afecção', 'Atestados', 'Total de Dias', 'Média de Dias']
                st.dataframe(cap_display, use_container_width=True, hide_index=True)

        st.markdown("---")
        col_left2, col_right2 = st.columns(2)

        with col_left2:
            st.markdown("<p class='section-title'>Funcionários com Mais Dias</p>", unsafe_allow_html=True)
            top_func = df.groupby('MAT')['DIAS'].sum().sort_values(ascending=False).head(10).reset_index()
            top_func.columns = ['Matrícula', 'Total de Dias']
            st.dataframe(top_func, use_container_width=True, hide_index=True)

        with col_right2:
            st.markdown("<p class='section-title'>CIDs com Maior Média de Dias</p>", unsafe_allow_html=True)
            top_cid_media = df.groupby('CID')['DIAS'].mean().sort_values(ascending=False).head(10).reset_index()
            top_cid_media.columns = ['CID', 'Média de Dias']
            # Aplica a formatação aos códigos CID
            top_cid_media['CID'] = top_cid_media['CID'].apply(get_cid_nome)
            st.dataframe(top_cid_media, use_container_width=True, hide_index=True)

        st.markdown("---")

        # Linha 5: Análise de Pareto (Funcionários)
        st.markdown("<p class='section-title'>Análise de Pareto - 80% dos Dias de Afastamento</p>", unsafe_allow_html=True)
        total_por_func = df.groupby('MAT')['DIAS'].sum().sort_values(ascending=False)
        acumulado = total_por_func.cumsum() / total_por_func.sum() * 100
        pareto = total_por_func[acumulado <= 80]

        st.write(f"**{len(pareto)} funcionários** (de um total de {df['MAT'].nunique()}) concentram **80% do total de dias** de afastamento.")
        if not pareto.empty:
            pareto_df = pareto.reset_index()
            pareto_df.columns = ['Matrícula', 'Total de Dias']
            st.dataframe(pareto_df, use_container_width=True, hide_index=True)

        st.markdown("---")

        # Linha 6: Tabela de Reincidência
        st.markdown("<p class='section-title'>Análise de Reincidência</p>", unsafe_allow_html=True)
        reincidentes = df['MAT'].value_counts()
        col_rec1, col_rec2 = st.columns(2)
        with col_rec1:
            st.metric("Funcionários com 1 atestado", (reincidentes == 1).sum())
        with col_rec2:
            st.metric("Funcionários com mais de 1 atestado", (reincidentes > 1).sum())

        st.markdown("---")

        # Linha 7: Visualização da Tabela Completa
        st.markdown("<p class='section-title'>Dados Completos do Período</p>", unsafe_allow_html=True)
        with st.expander("Clique para visualizar a tabela completa"):
            df_display = df.copy()
            df_display['CID (Nome)'] = df_display['CID'].apply(get_cid_nome)
            df_display['DATA'] = df_display['DATA'].dt.strftime('%d/%m/%Y')
            st.dataframe(df_display[['CID', 'CID (Nome)', 'MAT', 'DATA', 'DIAS', 'DIA_SEMANA', 'TIPO']], use_container_width=True, hide_index=True)

    elif df is not None and df.empty:
        st.warning(f"O arquivo {arquivo} foi carregado, mas está vazio.")

else:
    # Tela Inicial (sem mês selecionado)
    st.markdown("<h1>Dashboard de Controle de Afastamentos Médicos da Coordenação de Recursos Humanos do Litoral</h1>", unsafe_allow_html=True)
    st.markdown("""
    Este dashboard permite a análise detalhada dos atestados médicos por período.

    **Para iniciar:**
    1. Acesse o menu na barra lateral
    2. Selecione o período desejado
    3. Clique em "Carregar dados"

    Os dados serão processados e as análises serão exibidas automaticamente.
    """)

    st.markdown("---")
    st.markdown("**Períodos disponíveis:**")
    for mes in ARQUIVOS.keys():
        st.markdown(f"- {mes}")
