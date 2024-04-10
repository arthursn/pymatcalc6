#ifndef MATCALC_API_H
#define MATCALC_API_H

#include <cstdarg>
#include <stdexcept>
#include <vector>
#ifndef INCLUDE_DLL_IMPORT_H
#define MC_INDEX int
#include <dll_import.h>
#endif

#define STRLEN_MAX 1024

#ifndef MATCALC_DIR
#define MATCALC_DIR "C:/MatCalc"
#endif

#define EXECUTE_FMT_ARGS(function, fmt, ...) \
    do {                                     \
        char buf[STRLEN_MAX];                \
        sprintf(buf, fmt, ##__VA_ARGS__);    \
        function(buf);                       \
    } while (0)

void init(char* application_directory = MATCALC_DIR)
{
    MCC_InitializeExternalConstChar(application_directory, true);
    MCCOL_ProcessCommandLineInput("set-working-directory ./");
    EXECUTE_FMT_ARGS(MCCOL_ProcessCommandLineInput, "set-application-directory %s", application_directory);
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

#endif