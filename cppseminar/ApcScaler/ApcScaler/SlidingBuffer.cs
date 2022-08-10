using System.Collections;

namespace ApcScaler
{
    public class SlidingBuffer<T> : IEnumerable<T>
    {
        private readonly Queue<T> _queue;
        private readonly int _maxCount;

        public SlidingBuffer(int maxCount)
        {
            _maxCount = maxCount;
            _queue = new Queue<T>(maxCount);
        }

        public void Add(T item)
        {
            if (_queue.Count == _maxCount)
                _queue.Dequeue();
            _queue.Enqueue(item);
        }

        public IEnumerator<T> GetEnumerator()
        {
            return _queue.GetEnumerator();
        }

        IEnumerator IEnumerable.GetEnumerator()
        {
            return GetEnumerator();
        }

        public int MaxCount()
        { 
            return _maxCount;
        }

        public int ActCount()
        {
            return _queue.Count;
        }

        public decimal GetLatestAverage()
        {
            decimal average = -1.0M;
            decimal sum = 0.0M;
                
            if (_queue.Count == _maxCount)
            {
                foreach (T item in _queue)
                {
                    sum = sum + Convert.ToDecimal(item);
                }
            }

            average = sum / _maxCount;

            return average;
        }

        public bool IsAlwaysAbove(decimal threshold)
        {
            bool isAlwaysAbove = false;

            if (_queue.Count == _maxCount)
            {
                isAlwaysAbove = true;

                foreach (T item in _queue)
                {
                    if (Convert.ToDecimal(item) < threshold)
                    {
                        isAlwaysAbove = false;
                        break;
                    }
                }
            }

            return isAlwaysAbove;
        }

    }
}
