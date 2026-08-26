import clr
import sys
import json

#append assemblies dir
sys.path.append("C:\\ProgramData\\BHoM\\Assemblies")

#add reference to the BHoM_UI assembly
clr.AddReference("UI_Engine")
clr.AddReference("Serialiser_Engine")

from BH.Engine.UI import Query
from BH.Engine.Serialiser import Convert

INSTALLER_INFO = json.loads(Convert.ToJson(Query.Information()))