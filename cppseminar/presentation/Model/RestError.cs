using System.Collections.Generic;

namespace presentation.Model
{
    public class RestError
    {
        public string Title { get; set; }
        public int Status { get; set; }
        public Dictionary<string, List<string>> Errors { get; set; }

        public IList<string> GetErrors()
        {
            var allErrors = new List<string>();
            foreach (var errorList in Errors.Values)
            {
                foreach (string specificError in errorList)
                {
                    allErrors.Add(specificError);
                }
            }
            return allErrors;
        }
    }
}
