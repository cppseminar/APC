using System;

namespace presentation.Model
{
    public class OperationFailedException : Exception
    {
        public OperationFailedException()
        : base("Operation failed")
        {

        }
    }
}
