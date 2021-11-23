using BH.oM.Reflection.Attributes;
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace BH.Engine.Python
{
    public static partial class Modify
    {
        [Description("Adds quotes to a string (usually a file-path) if it contains spaces.")]
        [Input("path", "The file-path to add quotes around if necessary.")]
        [Output("path", "A usable file-path.")]
        public static string AddQuotesIfRequired(this string path)
        {
            return !string.IsNullOrWhiteSpace(path) ?
                path.Contains(" ") && (!path.StartsWith("\"") && !path.EndsWith("\"")) ?
                    "\"" + path + "\"" : path :
                    string.Empty;
        }
    }
}
