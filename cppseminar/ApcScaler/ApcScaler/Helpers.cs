﻿
namespace ApcScaler
{
    public static class Helpers
    {
        public static string ExtractErrorMessage(Exception e)
        {
            _ = e ?? throw new ArgumentNullException(nameof(e));

            string innerErrMessage = string.Empty;
            if (e.InnerException != null)
            {
                if (e.InnerException.Message != null)
                {
                    innerErrMessage = "(" + e.InnerException.Message + ")";
                }
            }

            string errMsg = string.Format("Error: {0} {1}",
                e.Message, innerErrMessage);

            return errMsg;
        }
    }
}
