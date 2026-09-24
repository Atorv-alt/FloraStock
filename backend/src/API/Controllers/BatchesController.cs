using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Authorization;
using Data.Repositories;
using Shared.Entities;
using Core.Services;
using Core.Interfaces;

namespace API.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    [Authorize]
    public class BatchesController : ControllerBase
    {
        private readonly IBatchRepository _batchRepository;
        private readonly ILogger<BatchesController> _logger;

        public BatchesController(
            IBatchRepository batchRepository,
            ILogger<BatchesController> logger)
        {
            _batchRepository = batchRepository;
            _logger = logger;
        }

        [HttpGet]
        public async Task<ActionResult<IEnumerable<Batch>>> GetAll()
        {
            try
            {
                var batches = await _batchRepository.GetAllAsync();
                return Ok(batches);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Ошибка при получении партий");
                return StatusCode(500, new { message = "Внутренняя ошибка сервера" });
            }
        }

        [HttpGet("{id}")]
        public async Task<ActionResult<Batch>> GetById(int id)
        {
            try
            {
                var batch = await _batchRepository.GetByIdAsync(id);
                if (batch == null)
                {
                    return NotFound(new { message = "Партия не найдена" });
                }
                return Ok(batch);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Ошибка при получении партии по ID: {Id}", id);
                return StatusCode(500, new { message = "Внутренняя ошибка сервера" });
            }
        }

        [HttpPost]
        public async Task<ActionResult<Batch>> Create([FromBody] CreateBatchRequest request)
        {
            try
            {
                if (string.IsNullOrEmpty(request.InvoiceNumber))
                {
                    return BadRequest(new { message = "Номер накладной обязателен" });
                }

                if (await _batchRepository.InvoiceNumberExistsAsync(request.InvoiceNumber))
                {
                    return Conflict(new { message = "Партия с таким номером накладной уже существует" });
                }

                var batch = new Batch
                {
                    SupplierID = request.SupplierId,
                    DeliveryDate = request.DeliveryDate,
                    InvoiceNumber = request.InvoiceNumber,
                    Quantity = request.Quantity,
                    CostPrice = request.CostPrice
                };

                var createdBatch = await _batchRepository.CreateAsync(batch);
                return CreatedAtAction(nameof(GetById), new { id = createdBatch.ID }, createdBatch);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Ошибка при создании партии");
                return StatusCode(500, new { message = "Внутренняя ошибка сервера" });
            }
        }

        [HttpPut("{id}")]
        public async Task<ActionResult<Batch>> Update(int id, [FromBody] UpdateBatchRequest request)
        {
            try
            {
                var existingBatch = await _batchRepository.GetByIdAsync(id);
                if (existingBatch == null)
                {
                    return NotFound(new { message = "Партия не найдена" });
                }

                if (string.IsNullOrEmpty(request.InvoiceNumber))
                {
                    return BadRequest(new { message = "Номер накладной обязателен" });
                }

                if (await _batchRepository.InvoiceNumberExistsAsync(request.InvoiceNumber, id))
                {
                    return Conflict(new { message = "Партия с таким номером накладной уже существует" });
                }

                existingBatch.SupplierID = request.SupplierId;
                existingBatch.DeliveryDate = request.DeliveryDate;
                existingBatch.InvoiceNumber = request.InvoiceNumber;
                existingBatch.Quantity = request.Quantity;
                existingBatch.CostPrice = request.CostPrice;

                var updatedBatch = await _batchRepository.UpdateAsync(existingBatch);
                return Ok(updatedBatch);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Ошибка при обновлении партии с ID: {Id}", id);
                return StatusCode(500, new { message = "Внутренняя ошибка сервера" });
            }
        }

        [HttpDelete("{id}")]
        public async Task<ActionResult> Delete(int id)
        {
            try
            {
                if (!await _batchRepository.ExistsAsync(id))
                {
                    return NotFound(new { message = "Партия не найдена" });
                }

                var result = await _batchRepository.DeleteAsync(id);
                if (!result)
                {
                    return BadRequest(new { message = "Не удалось удалить партию" });
                }

                return NoContent();
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Ошибка при удалении партии с ID: {Id}", id);
                return StatusCode(500, new { message = "Внутренняя ошибка сервера" });
            }
        }
    }

    public class CreateBatchRequest
    {
        public int? SupplierId { get; set; }
        public DateTime? DeliveryDate { get; set; }
        public string InvoiceNumber { get; set; } = string.Empty;
        public int? Quantity { get; set; }
        public decimal? CostPrice { get; set; }
    }

    public class UpdateBatchRequest
    {
        public int? SupplierId { get; set; }
        public DateTime? DeliveryDate { get; set; }
        public string InvoiceNumber { get; set; } = string.Empty;
        public int? Quantity { get; set; }
        public decimal? CostPrice { get; set; }
    }
}
