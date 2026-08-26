import os
import sys
import json

import clr

#append assemblies dir
sys.path.append(os.path.expandvars("%ProgramData%\\BHoM\\Assemblies"))

#add required CLR references (dotnet dlls)
clr.AddReference("UI_Engine")
clr.AddReference("Serialiser_Engine")

from BH.Engine.UI import Query
from BH.Engine.Serialiser import Convert

INSTALLER_INFO = json.loads(Convert.ToJson(Query.Information()))