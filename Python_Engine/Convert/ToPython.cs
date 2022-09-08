using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using BH.oM.Base.Attributes;

namespace BH.Engine.Python
{
    public static partial class Convert
    {
        [ToBeRemoved("5.3", "This method included in order to fool versioning into playing nicely.")]
        public static bool ToPython<T>(this T[,] input)
        {
            return false;
        }
    }
}
