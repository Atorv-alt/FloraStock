using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using Data;
using Microsoft.AspNetCore.Authorization;
using Data.Repositories;
using Shared.Entities;
using Core.Interfaces;

namespace API.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    [Authorize]
    public class SuppliersController : ControllerBase
    {
        private readonly ISupplierRepository _supplierRepository;
        private readonly AppDbContext _context;
        private readonly ILogger<SuppliersController> _logger;

        public SuppliersController(
            ISupplierRepository supplierRepository,
            Data.AppDbContext context,
            ILogger<SuppliersController> logger)
        {
            _supplierRepository = supplierRepository;
            _context = context;
            _logger = logger;
        }

        [HttpGet]
        public async Task<ActionResult<IEnumerable<Supplier>>> GetAll()
        {
            try
            {
                var suppliers = await _supplierRepository.GetAllAsync();
                return Ok(suppliers);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Ошибка при получении поставщиков");
                return StatusCode(500, new { message = "Внутренняя ошибка сервера" });
            }
        }

        [HttpGet("{id}")]
        public async Task<ActionResult<Supplier>> GetById(int id)
        {
            try
            {
                var supplier = await _supplierRepository.GetByIdAsync(id);
                if (supplier == null)
                {
                    return NotFound(new { message = "Поставщик не найден" });
                }
                return Ok(supplier);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Ошибка при получении поставщика по ID: {Id}", id);
                return StatusCode(500, new { message = "Внутренняя ошибка сервера" });
            }
        }

        [HttpPost]
        public async Task<ActionResult<Supplier>> Create([FromBody] Supplier supplier)
        {
            try
            {
                if (string.IsNullOrWhiteSpace(supplier.Name))
                {
                    return BadRequest(new { message = "Название поставщика обязательно" });
                }

                if (await _supplierRepository.NameExistsAsync(supplier.Name))
                {
                    return Conflict(new { message = "Поставщик с таким названием уже существует" });
                }

                var created = await _supplierRepository.CreateAsync(supplier);
                return CreatedAtAction(nameof(GetById), new { id = created.ID }, created);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Ошибка при создании поставщика");
                return StatusCode(500, new { message = "Внутренняя ошибка сервера" });
            }
        }

        [HttpPut("{id}")]
        public async Task<ActionResult<Supplier>> Update(int id, [FromBody] Supplier supplier)
        {
            try
            {
                var existing = await _supplierRepository.GetByIdAsync(id);
                if (existing == null)
                {
                    return NotFound(new { message = "Поставщик не найден" });
                }

                if (string.IsNullOrWhiteSpace(supplier.Name))
                {
                    return BadRequest(new { message = "Название поставщика обязательно" });
                }

                if (await _supplierRepository.NameExistsAsync(supplier.Name, id))
                {
                    return Conflict(new { message = "Поставщик с таким названием уже существует" });
                }

                existing.Name = supplier.Name;
                existing.PhoneNumber = supplier.PhoneNumber;
                existing.Email = supplier.Email;
                existing.Details = supplier.Details;
                existing.Address = supplier.Address;

                var updated = await _supplierRepository.UpdateAsync(existing);
                return Ok(updated);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Ошибка при обновлении поставщика: {Id}", id);
                return StatusCode(500, new { message = "Внутренняя ошибка сервера" });
            }
        }

        [HttpDelete("{id}")]
        public async Task<ActionResult> Delete(int id)
        {
            try
            {
                if (await _context.Batch.AnyAsync(b => b.SupplierID == id))
                {
                    return Conflict(new { message = "Нельзя удалить поставщика: есть связанные партии поставок" });
                }
                var deleted = await _supplierRepository.DeleteAsync(id);
                if (!deleted)
                {
                    return NotFound(new { message = "Поставщик не найден" });
                }
                return NoContent();
            }
            catch (Microsoft.EntityFrameworkCore.DbUpdateException dbEx)
            {
                _logger.LogWarning(dbEx, "Нарушение внешнего ключа при удалении");
                return Conflict(new { message = "Нельзя удалить поставщика: есть связанные партии поставок" });
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Ошибка при удалении поставщика: {Id}", id);
                return StatusCode(500, new { message = "Внутренняя ошибка сервера" });
            }
        }
    }
}