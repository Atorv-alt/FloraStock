using Microsoft.AspNetCore.Authorization;
using Microsoft.EntityFrameworkCore;
using Data;
using Microsoft.AspNetCore.Mvc;
using Core.Interfaces;
using Shared.Entities;

namespace API.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    [Authorize]
    public class EmployeesController : ControllerBase
    {
        private readonly IEmployeeRepository _employeeRepository;
        private readonly AppDbContext _context;
        private readonly ILogger<EmployeesController> _logger;

        public EmployeesController(
            IEmployeeRepository employeeRepository,
            Data.AppDbContext context,
            ILogger<EmployeesController> logger)
        {
            _employeeRepository = employeeRepository;
            _context = context;
            _logger = logger;
        }

        [HttpGet]
        [Authorize(Policy = "AdminOnly")]
        public async Task<ActionResult<IEnumerable<object>>> GetAll()
        {
            try
            {
                var employees = await _employeeRepository.GetAllAsync();
                return Ok(employees.Select(ToSafeShape));
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Ошибка при получении сотрудников");
                return StatusCode(500, new { message = "Внутренняя ошибка сервера" });
            }
        }

        [HttpGet("{id}")]
        [Authorize(Policy = "AdminOnly")]
        public async Task<ActionResult<object>> GetById(int id)
        {
            try
            {
                var employee = await _employeeRepository.GetByIdAsync(id);
                if (employee == null)
                {
                    return NotFound(new { message = "Сотрудник не найден" });
                }

                return Ok(ToSafeShape(employee));
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Ошибка при получении сотрудника с ID {Id}", id);
                return StatusCode(500, new { message = "Внутренняя ошибка сервера" });
            }
        }

        [HttpPost]
        [Authorize(Policy = "AdminOnly")]
        public async Task<ActionResult<object>> Create([FromBody] Employee employee)
        {
            try
            {
                if (string.IsNullOrWhiteSpace(employee.FullName))
                {
                    return BadRequest(new { message = "ФИО сотрудника обязательно" });
                }

                if (string.IsNullOrWhiteSpace(employee.Login))
                {
                    return BadRequest(new { message = "Логин обязателен" });
                }

                if (await _employeeRepository.LoginExistsAsync(employee.Login))
                {
                    return Conflict(new { message = "Сотрудник с таким логином уже существует" });
                }

                if (!string.IsNullOrEmpty(employee.Email) &&
                    await _employeeRepository.EmailExistsAsync(employee.Email))
                {
                    return Conflict(new { message = "Сотрудник с таким email уже существует" });
                }

                if (string.IsNullOrEmpty(employee.LoginPassword))
                {
                    return BadRequest(new { message = "Пароль обязателен" });
                }

                employee.LoginPassword = Core.Services.PasswordHasher.Hash(employee.LoginPassword);

                var createdEmployee = await _employeeRepository.CreateAsync(employee);
                return CreatedAtAction(nameof(GetById), new { id = createdEmployee.ID }, ToSafeShape(createdEmployee));
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Ошибка при создании сотрудника");
                return StatusCode(500, new { message = "Внутренняя ошибка сервера" });
            }
        }

        [HttpPut("{id}")]
        [Authorize(Policy = "AdminOnly")]
        public async Task<ActionResult<object>> Update(int id, [FromBody] Employee employee)
        {
            try
            {
                if (id != employee.ID)
                {
                    return BadRequest(new { message = "ID в пути не совпадает с ID в теле запроса" });
                }

                var existing = await _employeeRepository.GetByIdAsync(id);
                if (existing == null)
                {
                    return NotFound(new { message = "Сотрудник не найден" });
                }

                if (!string.IsNullOrWhiteSpace(employee.Login) &&
                    await _employeeRepository.LoginExistsAsync(employee.Login, id))
                {
                    return Conflict(new { message = "Сотрудник с таким логином уже существует" });
                }

                if (!string.IsNullOrEmpty(employee.Email) &&
                    await _employeeRepository.EmailExistsAsync(employee.Email, id))
                {
                    return Conflict(new { message = "Сотрудник с таким email уже существует" });
                }

                existing.FullName = employee.FullName;
                existing.Position = employee.Position;
                existing.PhoneNumber = employee.PhoneNumber;
                existing.Email = employee.Email;
                existing.Login = employee.Login;
                existing.AccessLevel = employee.AccessLevel;

                // Пустой пароль = не менять (иначе затрем хеш)
                if (!string.IsNullOrEmpty(employee.LoginPassword))
                {
                    existing.LoginPassword = Core.Services.PasswordHasher.Hash(employee.LoginPassword);
                }

                var updatedEmployee = await _employeeRepository.UpdateAsync(existing);
                return Ok(ToSafeShape(updatedEmployee));
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Ошибка при обновлении сотрудника с ID {Id}", id);
                return StatusCode(500, new { message = "Внутренняя ошибка сервера" });
            }
        }

        [HttpDelete("{id}")]
        [Authorize(Policy = "AdminOnly")]
        public async Task<ActionResult> Delete(int id)
        {
            try
            {
                if (await _context.Order.AnyAsync(o => o.EmployeeID == id))
                {
                    return Conflict(new { message = "Нельзя удалить сотрудника: есть связанные заказы" });
                }
                var deleted = await _employeeRepository.DeleteAsync(id);
                if (!deleted)
                {
                    return NotFound(new { message = "Сотрудник не найден" });
                }
                return NoContent();
            }
            catch (Microsoft.EntityFrameworkCore.DbUpdateException dbEx)
            {
                _logger.LogWarning(dbEx, "Нарушение внешнего ключа при удалении");
                return Conflict(new { message = "Нельзя удалить сотрудника: есть связанные заказы" });
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Ошибка при удалении сотрудника с ID {Id}", id);
                return StatusCode(500, new { message = "Внутренняя ошибка сервера" });
            }
        }

        // Хеш пароля никогда не отдаём наружу
        private static object ToSafeShape(Employee e) => new
        {
            id = e.ID,
            fullName = e.FullName,
            position = e.Position,
            phoneNumber = e.PhoneNumber,
            email = e.Email,
            login = e.Login,
            accessLevel = e.AccessLevel
        };
    }
}
