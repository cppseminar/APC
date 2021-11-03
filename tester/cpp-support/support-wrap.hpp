#pragma once

extern "C" {
#include "support.h"
}

#include <vector>
#include <string>
#include <stdexcept>
#include <chrono>
#include <optional>
#include <memory>
#include <filesystem>
#include <string.h>

class Process {
    public:
        Process(const std::string& name, const std::vector<std::string>& params) {
            std::vector<const char*> copy;
            for (const auto& i : params) {
                copy.push_back(i.c_str());
            }

            if (process_create(name.c_str(), copy.data(), copy.size(), &p) < 0) {
                throw std::runtime_error("Cannot create process (see std err).");
            }
        }

        ~Process() {
            process_close(&p);
        }

        void CloseStdIn() {
            process_close_stdin(&p);
        }

        // -1 on timeout, otherwise process exit code
        int Wait(std::chrono::seconds timeout) {
            int status = process_wait(&p, timeout.count());
            if (status < 0) {
                if (errno == ETIME) {
                    return -1;
                }

                throw std::runtime_error("Cannot wait for process(see std err).");
            }

            return status;
        }

        bool SendLine(const std::string& line) {
            return process_send_line(&p, line.c_str()) >= 0;
        }

        std::optional<std::string> ReadLine(std::chrono::seconds timeout) {
            std::unique_ptr<char, decltype(&std::free)> data{
                process_read_line(&p, timeout.count()),
                &std::free 
            };
            
            if (data) {
                // trim trailing whitespace
                std::string result = data.get();
                auto it = std::find_if(result.rbegin(), result.rend(), [](auto c) { return !isspace(c); });
                result.resize(std::distance(result.begin(), it.base()));

                return result;
            }

            return std::nullopt;
        }
private:
    process_t p;
};

enum class TmpFileMode {
    Rw = TFM_RW, 
    Ro = TFM_RO, 
    Wo = TFM_WO,
};

inline std::filesystem::path CreateTempFile(const std::vector<char>& data, TmpFileMode mode = TmpFileMode::Rw) {
    std::unique_ptr<char, decltype(&std::free)> file{
        create_tmp_file(data.data(), data.size(), static_cast<tmp_file_mode>(mode)),
        &std::free 
    };

    if (file == nullptr) {
        throw std::runtime_error("Cannot create temp file");
    }

    return std::filesystem::path(file.get(), file.get() + strlen(file.get()));
}

inline std::filesystem::path CreateTempFile(TmpFileMode mode = TmpFileMode::Rw) {
    return CreateTempFile(std::vector<char>{}, mode);
}


inline std::filesystem::path CreateTempFile(const std::vector<std::string>& lines, TmpFileMode mode = TmpFileMode::Rw) {
    std::string data;
    for (const auto& i : lines) {
        data += i;
        data += '\n';
    }

    return CreateTempFile(std::vector<char>{data.begin(), data.end()}, mode);
}

inline std::vector<std::string> ReadLinesFromFile(const std::filesystem::path& path) {
    std::ifstream f(path);
    std::vector<std::string> result;

    std::string to;
    while (std::getline(f, to, '\n')) {
        result.push_back(std::move(to));
    }

    return result;
}

inline void RemoveFile(const std::filesystem::path& path) {
    if (!remove_file(path.c_str())) {
        throw std::runtime_error("Cannot delete file");
    }
}

inline std::string GetSubmissionPath() {
    const char* submission = std::getenv("SUBMISSIONPATH");
    if (submission == nullptr) {
        submission = "./submission";
    }

    return submission;
}

inline std::filesystem::path GetData(const std::string& filename) {
    const char* data_path = std::getenv("DATAPATH");
    if (data_path == nullptr) {
        throw std::runtime_error("Cannot get DATAPATH env");
    }

    return std::filesystem::path(data_path) / filename;
}