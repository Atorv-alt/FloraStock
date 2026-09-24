using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Core.Interfaces;
using Shared.Entities;

namespace API.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class AuthController : ControllerBase
    {
        private readonly IAuthService _authService;
        private readonly IEmployeeRepository _employeeRepository;
        private readonly ILogger<AuthController> _logger;

        public AuthController(
            IAuthService authService,
            IEmployeeRepository employeeRepository,
            ILogger<AuthController> logger)
        {
            _authService = authService;
            _employeeRepository = employeeRepository;
            _logger = logger;
        }

        [HttpPost("login")]
        public async Task<IActionResult> Login([FromBody] LoginRequest request)
        {
            try
            {
                _logger.LogInformation("Получен запрос на вход: {Login}", request.Login);
                
                if (string.IsNullOrEmpty(request.Login) || string.IsNullOrEmpty(request.Password))
                {
                    _logger.LogWarning("Пустой логин или пароль");
                    return BadRequest(new { message = "Логин и пароль обязательны" });
                }

                _logger.LogInformation("Начало аутентификации для: {Login}", request.Login);
                var token = await _authService.AuthenticateAsync(request.Login, request.Password);
                _logger.LogInformation("Результат аутентификации: {Token}", token == null ? "null" : "успешно");
                
                if (string.IsNullOrEmpty(token))
                {
                    return Unauthorized(new { message = "Неверный логин или пароль" });
                }

                var employee = await _employeeRepository.GetByLoginAsync(request.Login);
                
                return Ok(new 
                { 
                    token = token,
                    employee = new 
                    {
                        id = employee!.ID,
                        fullName = employee.FullName,
                        position = employee.Position,
                        accessLevel = employee.AccessLevel
                    }
                });
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Ошибка при входе в систему");
                return StatusCode(500, new { message = "Внутренняя ошибка сервера" });
            }
        }

        [HttpPost("refresh")]
        [Authorize]
        public async Task<IActionResult> RefreshToken()
        {
            try
            {
                var userIdClaim = User.FindFirst("UserId")?.Value;
                if (string.IsNullOrEmpty(userIdClaim) || !int.TryParse(userIdClaim, out var userId))
                {
                    return Unauthorized();
                }

                var employee = await _employeeRepository.GetByIdAsync(userId);
                if (employee == null)
                {
                    return Unauthorized();
                }

                var token = _authService.GenerateTokenAsync(employee);
                
                return Ok(new { token });
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Ошибка при обновлении токена");
                return StatusCode(500, new { message = "Внутренняя ошибка сервера" });
            }
        }

        [HttpPost("change-password")]
        [Authorize]
        public async Task<IActionResult> ChangePassword([FromBody] ChangePasswordRequest request)
        {
            try
            {
                var userIdClaim = User.FindFirst("UserId")?.Value;
                if (string.IsNullOrEmpty(userIdClaim) || !int.TryParse(userIdClaim, out var userId))
                {
                    return Unauthorized();
                }

                if (string.IsNullOrEmpty(request.CurrentPassword) || string.IsNullOrEmpty(request.NewPassword))
                {
                    return BadRequest(new { message = "Текущий и новый пароли обязательны" });
                }

                var result = await _authService.ChangePasswordAsync(userId, request.CurrentPassword, request.NewPassword);
                
                if (!result)
                {
                    return BadRequest(new { message = "Неверный текущий пароль" });
                }

                return Ok(new { message = "Пароль успешно изменен" });
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Ошибка при изменении пароля");
                return StatusCode(500, new { message = "Внутренняя ошибка сервера" });
            }
        }

        [HttpGet("me")]
        [Authorize]
        public async Task<IActionResult> GetCurrentUser()
        {
            try
            {
                var userIdClaim = User.FindFirst("UserId")?.Value;
                if (string.IsNullOrEmpty(userIdClaim) || !int.TryParse(userIdClaim, out var userId))
                {
                    return Unauthorized();
                }

                var employee = await _employeeRepository.GetByIdAsync(userId);
                if (employee == null)
                {
                    return Unauthorized();
                }

                return Ok(new 
                {
                    ID = employee.ID,
                    fullName = employee.FullName,
                    position = employee.Position,
                    accessLevel = employee.AccessLevel,
                    email = employee.Email,
                    phoneNumber = employee.PhoneNumber
                });
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Ошибка при получении текущего пользователя");
                return StatusCode(500, new { message = "Внутренняя ошибка сервера" });
            }
        }
    }

    public class LoginRequest
    {
        public string Login { get; set; } = string.Empty;
        public string Password { get; set; } = string.Empty;
    }

    public class ChangePasswordRequest
    {
        public string CurrentPassword { get; set; } = string.Empty;
        public string NewPassword { get; set; } = string.Empty;
    }
}