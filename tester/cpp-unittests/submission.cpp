#include <string>
#include <iostream>
#include <fstream>
#include <array>
#include <optional>
#include <assert.h>

constexpr const std::string_view CHECK = "--check";
constexpr const std::string_view INPUT_PARAM = "-i";
constexpr const std::string_view OUTPUT_PARAM = "-o";

class SudokuBoard
{
public:
    SudokuBoard() = default;

    SudokuBoard(const std::string& sdm)
    {
        assert(CheckSdmFormat(sdm));

        for (size_t i = 0; i < 9; ++i)
        {
            for (size_t j = 0; j < 9; ++j)
            {
                m_board[i][j] = 0;

                char c = sdm[i * 9 + j];
                if (c != '.')
                {
                    m_board[i][j] = c - '0';
                }
            }
        }
    }

    std::optional<SudokuBoard> Solve()
    {
        auto copy = *this;
        if (copy.SolveThis())
            return copy;

        return std::nullopt;
    }

    static bool CheckSdmFormat(const std::string& sdm)
    {
        if (sdm.size() != 81)
            return false;

        for (auto c : sdm)
        {
            if (c != '.' && (c < '0' || c > '9'))
                return false;
        }

        return true;
    }

    friend std::ostream& operator<<(std::ostream&, const SudokuBoard&);
private:
    static constexpr size_t BOX = 3;
    static constexpr size_t SIZE = BOX * BOX;

    std::array<std::array<uint8_t, SIZE>, SIZE> m_board;

    bool Check()
    {
        class Checker
        {
        public:
            bool Add(uint8_t num)
            {
                if (num == 0)
                    return true;

                if (m_set[num - 1])
                    return false;

                m_set[num - 1] = true;
                return true;
            }

        private:
            std::array<bool, SIZE> m_set = {};
        };

        // check horizontal and vertical
        for (size_t i = 0; i < SIZE; ++i)
        {
            Checker checkRow;
            Checker checkColumn;
            Checker checkBox;
            for (size_t j = 0; j < SIZE; ++j)
            {
                if (!checkRow.Add(m_board[i][j]))
                    return false;

                if (!checkColumn.Add(m_board[j][i]))
                    return false;

                // this take me something like 20minutes to do...
                size_t ii = (i % BOX) * BOX + (j / BOX);
                size_t jj = (i / BOX) * BOX + (j % BOX);
                if (!checkBox.Add(m_board[ii][jj]))
                    return false;
            }
        }

        return true;
    }

    bool SolveThis()
    {
        return SolveThisRecursive(0, 0);
    }

    bool SolveThisRecursive(size_t x, size_t y)
    {
        if (y >= SIZE)
            return Check(); // no more room to advance return the status

        if (x >= SIZE)
            return SolveThisRecursive(0, y + 1); // if X is out of bounds advance to next column

        if (m_board[x][y] != 0)
            return SolveThisRecursive(x + 1, y); // advance to next cell (out of bounds is handled before)

        for (uint8_t i = 0; i < SIZE; ++i)
        {
            m_board[x][y] = i + 1;
            if (Check() && SolveThisRecursive(x + 1, y))
                return true;
        }

        m_board[x][y] = 0; // reset back to allow backtrack
        return false;
    }
};

std::ostream& operator<<(std::ostream& os, const SudokuBoard& board)
{
    for (const auto& a : board.m_board)
        for (const auto& b : a)
            os << static_cast<char>('0' + b);
    return os;
}

std::istream& operator>>(std::istream& is, SudokuBoard& sudoku)
{
    std::string line;
    if (!std::getline(is, line))
        return is;

    if (!SudokuBoard::CheckSdmFormat(line))
    {
        is.setstate(std::ios::failbit);
        return is;
    }

    sudoku = SudokuBoard(line);
    return is;
}

enum class Mode
{
    Invalid,
    Solve,
    Check,
};

struct ConsoleParameters
{
    Mode mode; // if Invalid, then parameters were incorrect
    std::string input; // if empty then stdin
    std::string output; // if empty then stdout
};

ConsoleParameters GetParams(int argc, char** argv)
{
    ConsoleParameters result{ Mode::Invalid, {}, {} };

    if (argc == 3 && argv[1] == CHECK)
    {
        // should be --check <input file>
        result.mode = Mode::Check;
        result.input = argv[2];
    }

    if (argc % 2 == 1) // standard -i -o
    {
        for (int i = 1; i < argc; i += 2)
        {
            if (argv[i] == INPUT_PARAM)
            {
                result.input = argv[i + 1];
            }
            else if (argv[i] == OUTPUT_PARAM)
            {
                result.output = argv[i + 1];
            }
            else
            {
                return result; // invalid
            }
        }

        result.mode = Mode::Solve; // everything OK
    }

    return result;
}

bool Solve(std::istream& input, std::ostream& output)
{
    SudokuBoard board;
    while (input >> board)
    {
        if (auto result = board.Solve(); result)
        {
            output << *result;
        }

        output << '\n'; // if no solution empty line is written
    }

    if (!input.eof())
    {
        std::cerr << "Error in input stream/file" << std::endl;
        return false;
    }

    if (!output)
    {
        std::cerr << "Error in output stream/file" << std::endl;
        return false;
    }

    return true;
}

bool Solve(const std::string& inputFile, const std::string& outputFile)
{
    std::ifstream input;
    if (!inputFile.empty())
    {
        input.open(inputFile);
    }

    std::ofstream output;
    if (!outputFile.empty())
    {
        output.open(outputFile);
    }

    return Solve(inputFile.empty() ? std::cin : input, outputFile.empty() ? std::cout : output);
}

int main(int argc, char** argv)
{
    // let's make it fast
    std::ios::sync_with_stdio(false);

    auto params = GetParams(argc, argv);

    switch (params.mode)
    {
    case Mode::Invalid:
        std::cout << "Invalid parameters. Usage \n";
        std::cout << "\t--check <filename>   will check sdx file\n";
        std::cout << "\t-i <input>           sets the input file (default stdin)\n";
        std::cout << "\t-o <output>          sets the output file (default stdout)\n";
        return 1;

    case Mode::Solve:
        return Solve(params.input, params.output) ? EXIT_SUCCESS : EXIT_FAILURE;

    default:
        std::cerr << "Unexpected error.\n";
        return EXIT_SUCCESS;
    }
}