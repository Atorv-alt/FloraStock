using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Data;
using Microsoft.EntityFrameworkCore;

namespace API.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    [Authorize]
    public class TestController : ControllerBase
    {
        private readonly AppDbContext _context;

        public TestController(AppDbContext context)
        {
            _context = context;
        }

        [HttpGet("employees")]
        public async Task<IActionResult> GetEmployees()
        {
            try
            {
                // Хеши паролей наружу не отдаём
                var employees = await _context.Employee
                    .Select(e => new { e.ID, e.FullName, e.Login, e.Email, e.AccessLevel })
                    .ToListAsync();
                
                return Ok(new { 
                    message = "Test successful", 
                    count = employees.Count,
                    employees = employees 
                });
            }
            catch (Exception ex)
            {
                return StatusCode(500, new { 
                    message = "Database error", 
                    error = ex.Message 
                });
            }
        }

        [HttpGet("employee/{fullName}")]
        public async Task<IActionResult> GetEmployee(string fullName)
        {
            try
            {
                var employee = await _context.Employee
                    .Where(e => e.FullName == fullName)
                    .Select(e => new { e.ID, e.FullName, e.Login, e.Email, e.AccessLevel })
                    .FirstOrDefaultAsync();
                
                if (employee == null)
                {
                    return NotFound(new { message = "Employee not found", fullName });
                }
                
                return Ok(employee);
            }
            catch (Exception ex)
            {
                return StatusCode(500, new { 
                    message = "Database error", 
                    error = ex.Message 
                });
            }
        }
    }
}
