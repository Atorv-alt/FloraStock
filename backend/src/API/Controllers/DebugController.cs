using Microsoft.AspNetCore.Mvc;
using Core.Interfaces;
using Shared.Entities;

namespace API.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class DebugController : ControllerBase
    {
        private readonly IAuthService _authService;
        private readonly IEmployeeRepository _employeeRepository;

        public DebugController(IAuthService authService, IEmployeeRepository employeeRepository)
        {
            _authService = authService;
            _employeeRepository = employeeRepository;
        }

        [HttpGet("auth/{login}/{password}")]
        public async Task<IActionResult> DebugAuth(string login, string password)
        {
            try
            {
                // Шаг 1: Проверяем, находим ли пользователя
                var employee = await _employeeRepository.GetByLoginAsync(login);
                
                if (employee == null)
                {
                    return Ok(new { 
                        step = "employee_not_found", 
                        login = login,
                        message = "Employee not found" 
                    });
                }

                // Шаг 2: Проверяем пароль
                var passwordMatch = employee.LoginPassword == password;
                
                if (!passwordMatch)
                {
                    return Ok(new { 
                        step = "password_mismatch", 
                        login = login,
                        employeePassword = employee.LoginPassword,
                        providedPassword = password,
                        message = "Password does not match" 
                    });
                }

                // Шаг 3: Проверяем аутентификацию
                var token = await _authService.AuthenticateAsync(login, password);
                
                return Ok(new { 
                    step = "auth_result", 
                    login = login,
                    employeeId = employee.ID,
                    employeeName = employee.FullName,
                    token = token,
                    tokenIsNull = token == null,
                    message = token == null ? "Authentication failed" : "Authentication successful"
                });
            }
            catch (Exception ex)
            {
                return StatusCode(500, new { 
                    step = "exception", 
                    login = login,
                    error = ex.Message,
                    stackTrace = ex.StackTrace
                });
            }
        }
    }
}
