using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Core.Interfaces;

namespace API.Controllers
{
    // Диагностический контроллер: только для администраторов.
    // Пароли/хеши и стектрейсы наружу не отдаются.
    [ApiController]
    [Route("api/[controller]")]
    [Authorize(Policy = "AdminOnly")]
    public class DebugController : ControllerBase
    {
        private readonly IAuthService _authService;
        private readonly IEmployeeRepository _employeeRepository;

        public DebugController(IAuthService authService, IEmployeeRepository employeeRepository)
        {
            _authService = authService;
            _employeeRepository = employeeRepository;
        }

        public class DebugAuthRequest
        {
            public string Login { get; set; } = string.Empty;
            public string Password { get; set; } = string.Empty;
        }

        [HttpPost("auth")]
        public async Task<IActionResult> DebugAuth([FromBody] DebugAuthRequest request)
        {
            try
            {
                // Шаг 1: Проверяем, находим ли пользователя
                var employee = await _employeeRepository.GetByLoginAsync(request.Login);

                if (employee == null)
                {
                    return Ok(new
                    {
                        step = "employee_not_found",
                        login = request.Login,
                        message = "Employee not found"
                    });
                }

                // Шаг 2: Проверяем аутентификацию (без раскрытия хешей)
                var token = await _authService.AuthenticateAsync(request.Login, request.Password);

                return Ok(new
                {
                    step = "auth_result",
                    login = request.Login,
                    employeeId = employee.ID,
                    employeeName = employee.FullName,
                    authenticated = token != null,
                    message = token == null ? "Authentication failed" : "Authentication successful"
                });
            }
            catch (Exception ex)
            {
                return StatusCode(500, new
                {
                    step = "exception",
                    login = request.Login,
                    error = ex.Message
                });
            }
        }
    }
}
