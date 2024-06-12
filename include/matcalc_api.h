#ifndef MATCALC_API_H
#define MATCALC_API_H

#include <cstdarg>
#include <cstring>
#include <dylib.hpp>
#include <filesystem>
#include <functional>
#include <stdexcept>
#include <vector>

#define STRLEN_MAX 1024

#define EXECUTE_FMT_ARGS(function, fmt, ...) \
    do {                                     \
        char buf[STRLEN_MAX];                \
        sprintf(buf, fmt, ##__VA_ARGS__);    \
        function(buf);                       \
    } while (0)

class MatCalcAPI {
private:
    dylib* mvpLibMatCalc = nullptr;

    char mvApplicationDirectory[STRLEN_MAX];

    std::function<bool(const char*, bool)> MCC_InitializeExternalConstChar;
    std::function<int(char*)> MCCOL_ProcessCommandLineInput;
    std::function<int(char*)> MCCOL_ProcessCommandLineInputNewColine;
    std::function<int(bool, int)> MCC_CalcEquilibrium;
    std::function<double(double, bool)> MCC_SetTemperature;
    std::function<double(char*)> MCC_GetMCVariable;

    void dynamicallyLoadFunctions(dylib* pLibMatCalc)
    {
        MCC_InitializeExternalConstChar = pLibMatCalc->get_function<bool(const char*, bool)>("MCC_InitializeExternalConstChar");
        MCCOL_ProcessCommandLineInput = pLibMatCalc->get_function<int(char*)>("MCCOL_ProcessCommandLineInput");
        MCCOL_ProcessCommandLineInputNewColine = pLibMatCalc->get_function<int(char*)>("MCCOL_ProcessCommandLineInputNewColine");
        MCC_CalcEquilibrium = pLibMatCalc->get_function<int(bool, int)>("MCC_CalcEquilibrium");
        MCC_SetTemperature = pLibMatCalc->get_function<double(double, bool)>("MCC_SetTemperature");
        MCC_GetMCVariable = pLibMatCalc->get_function<double(char*)>("MCC_GetMCVariable");
    }

public:
    MatCalcAPI(const char* application_directory = "C:/MatCalc")
    {
        strcpy(mvApplicationDirectory, application_directory);

        std::filesystem::current_path(mvApplicationDirectory);

        mvpLibMatCalc = new dylib(mvApplicationDirectory, "mc_core");

        dynamicallyLoadFunctions(mvpLibMatCalc);
    }

    ~MatCalcAPI()
    {
        delete mvpLibMatCalc;
    }

    void init()
    {
        MCC_InitializeExternalConstChar(mvApplicationDirectory, true);
        MCCOL_ProcessCommandLineInput("set-working-directory ./");
        EXECUTE_FMT_ARGS(MCCOL_ProcessCommandLineInput, "set-application-directory %s", mvApplicationDirectory);
    }

    void execute_command(char* cmd)
    {
        int error_code = MCCOL_ProcessCommandLineInput(cmd);
        if (error_code != 0) {
            char error_message[STRLEN_MAX];
            sprintf(error_message, "Err nr %d while executing '%s'", error_code, cmd);
            throw std::runtime_error(error_message);
        }
    }

    void execute_command_new_coline(char* cmd)
    {
        int error_code = MCCOL_ProcessCommandLineInputNewColine(cmd);
        if (error_code != 0) {
            char error_message[STRLEN_MAX];
            sprintf(error_message, "Err nr %d while executing '%s'", error_code, cmd);
            throw std::runtime_error(error_message);
        }
    }

    void calculate_equilibrium()
    {
        int error_code = MCC_CalcEquilibrium(false, 0);
        if (error_code != 0) {
            char error_message[STRLEN_MAX];
            sprintf(error_message, "Err nr %d while calculating equilibrium", error_code);
            throw std::runtime_error(error_message);
        }
    }

    void set_temperature_kelvin(double temperature_kelvin)
    {
        MCC_SetTemperature(temperature_kelvin, false);
    }

    void set_element_mole_fraction(const char* element_symbol, double value)
    {
        EXECUTE_FMT_ARGS(execute_command, "enter-composition X %s=%g", element_symbol, value);
    }

    void set_element_weight_fraction(char* element_symbol, double value)
    {
        EXECUTE_FMT_ARGS(execute_command, "enter-composition W %s=%g", element_symbol, value);
    }

    void set_element_site_fraction(char* element_symbol, double value)
    {
        EXECUTE_FMT_ARGS(execute_command, "enter-composition U %s=%g", element_symbol, value);
    }

    double get_variable(char* variable)
    {
        return MCC_GetMCVariable(variable);
    }
};

#endif