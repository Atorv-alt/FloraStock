using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Core.Interfaces;
using Shared.Entities;

namespace API.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    [Authorize]
    public class InventoryController : ControllerBase
    {
        private readonly IInventoryRepository _inventoryRepository;
        private readonly IProductRepository _productRepository;
        private readonly IBatchRepository _batchRepository;
        private readonly ILogger<InventoryController> _logger;

        public InventoryController(
            IInventoryRepository inventoryRepository,
            IProductRepository productRepository,
            IBatchRepository batchRepository,
            ILogger<InventoryController> logger)
        {
            _inventoryRepository = inventoryRepository;
            _productRepository = productRepository;
            _batchRepository = batchRepository;
            _logger = logger;
        }

        [HttpGet]
        public async Task<ActionResult<IEnumerable<Inventory>>> GetAll()
        {
            try
            {
                var inventory = await _inventoryRepository.GetAllAsync();
                return Ok(inventory);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Ошибка при получении складских остатков");
                return StatusCode(500, new { message = "Внутренняя ошибка сервера" });
            }
        }

        [HttpGet("{id}")]
        public async Task<ActionResult<Inventory>> GetById(int id)
        {
            try
            {
                var inventory = await _inventoryRepository.GetByIdAsync(id);
                if (inventory == null)
                {
                    return NotFound(new { message = "Складская позиция не найдена" });
                }

                return Ok(inventory);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Ошибка при получении складской позиции с ID: {Id}", id);
                return StatusCode(500, new { message = "Внутренняя ошибка сервера" });
            }
        }

        [HttpGet("product/{productId}")]
        public async Task<ActionResult<IEnumerable<Inventory>>> GetByProduct(int productId)
        {
            try
            {
                if (!await _productRepository.ExistsAsync(productId))
                {
                    return NotFound(new { message = "Товар не найден" });
                }

                var inventory = await _inventoryRepository.GetByProductAsync(productId);
                return Ok(inventory);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Ошибка при получении складских остатков по товару");
                return StatusCode(500, new { message = "Внутренняя ошибка сервера" });
            }
        }

        [HttpGet("batch/{batchId}")]
        public async Task<ActionResult<IEnumerable<Inventory>>> GetByBatch(int batchId)
        {
            try
            {
                if (!await _batchRepository.ExistsAsync(batchId))
                {
                    return NotFound(new { message = "Партия не найдена" });
                }

                var inventory = await _inventoryRepository.GetByBatchAsync(batchId);
                return Ok(inventory);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Ошибка при получении складских остатков по партии");
                return StatusCode(500, new { message = "Внутренняя ошибка сервера" });
            }
        }

        [HttpGet("low-stock")]
        public async Task<ActionResult<IEnumerable<Inventory>>> GetLowStock([FromQuery] int threshold = 10)
        {
            try
            {
                var inventory = await _inventoryRepository.GetLowStockAsync(threshold);
                return Ok(inventory);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Ошибка при получении товаров с низким остатком");
                return StatusCode(500, new { message = "Внутренняя ошибка сервера" });
            }
        }

        [HttpGet("expiring-soon")]
        public async Task<ActionResult<IEnumerable<Inventory>>> GetExpiringSoon([FromQuery] int daysThreshold = 7)
        {
            try
            {
                var inventory = await _inventoryRepository.GetExpiringSoonAsync(daysThreshold);
                return Ok(inventory);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Ошибка при получении товаров с истекающим сроком годности");
                return StatusCode(500, new { message = "Внутренняя ошибка сервера" });
            }
        }

        [HttpPost]
        public async Task<ActionResult<Inventory>> Create([FromBody] CreateInventoryRequest request)
        {
            try
            {
                if (request.ProductId.HasValue && !await _productRepository.ExistsAsync(request.ProductId.Value))
                {
                    return BadRequest(new { message = "Указанный товар не существует" });
                }

                if (request.BatchId.HasValue && !await _batchRepository.ExistsAsync(request.BatchId.Value))
                {
                    return BadRequest(new { message = "Указанная партия не существует" });
                }

                if (request.Quantity < 0)
                {
                    return BadRequest(new { message = "Количество не может быть отрицательным" });
                }

                var inventory = new Inventory
                {
                    ProductId = request.ProductId,
                    BatchId = request.BatchId,
                    Quantity = request.Quantity,
                    ReceiptDate = request.ReceiptDate?.Date ?? DateTime.Today,
                    StorageLocation = request.StorageLocation,
                    StorageTemperature = request.StorageTemperature,
                    HumidityLevel = request.HumidityLevel
                };

                var createdInventory = await _inventoryRepository.CreateAsync(inventory);
                return CreatedAtAction(nameof(GetById), new { id = createdInventory.ID }, createdInventory);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Ошибка при создании складской позиции");
                return StatusCode(500, new { message = "Внутренняя ошибка сервера" });
            }
        }

        [HttpPut("{id}")]
        public async Task<ActionResult<Inventory>> Update(int id, [FromBody] UpdateInventoryRequest request)
        {
            try
            {
                var existingInventory = await _inventoryRepository.GetByIdAsync(id);
                if (existingInventory == null)
                {
                    return NotFound(new { message = "Складская позиция не найдена" });
                }

                if (request.ProductId.HasValue && !await _productRepository.ExistsAsync(request.ProductId.Value))
                {
                    return BadRequest(new { message = "Указанный товар не существует" });
                }

                if (request.BatchId.HasValue && !await _batchRepository.ExistsAsync(request.BatchId.Value))
                {
                    return BadRequest(new { message = "Указанная партия не существует" });
                }

                if (request.Quantity.HasValue && request.Quantity.Value < 0)
                {
                    return BadRequest(new { message = "Количество не может быть отрицательным" });
                }

                existingInventory.ProductId = request.ProductId ?? existingInventory.ProductId;
                existingInventory.BatchId = request.BatchId ?? existingInventory.BatchId;
                existingInventory.Quantity = request.Quantity ?? existingInventory.Quantity;
                existingInventory.ReceiptDate = request.ReceiptDate?.Date ?? existingInventory.ReceiptDate;
                existingInventory.StorageLocation = request.StorageLocation ?? existingInventory.StorageLocation;
                existingInventory.StorageTemperature = request.StorageTemperature ?? existingInventory.StorageTemperature;
                existingInventory.HumidityLevel = request.HumidityLevel ?? existingInventory.HumidityLevel;

                var updatedInventory = await _inventoryRepository.UpdateAsync(existingInventory);
                return Ok(updatedInventory);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Ошибка при обновлении складской позиции с ID: {Id}", id);
                return StatusCode(500, new { message = "Внутренняя ошибка сервера" });
            }
        }

        [HttpPut("{id}/quantity")]
        public async Task<ActionResult> UpdateQuantity(int id, [FromBody] UpdateQuantityRequest request)
        {
            try
            {
                if (request.Quantity < 0)
                {
                    return BadRequest(new { message = "Количество не может быть отрицательным" });
                }

                var result = await _inventoryRepository.UpdateQuantityAsync(id, request.Quantity);
                if (!result)
                {
                    return NotFound(new { message = "Складская позиция не найдена" });
                }

                return NoContent();
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Ошибка при обновлении количества складской позиции");
                return StatusCode(500, new { message = "Внутренняя ошибка сервера" });
            }
        }

        [HttpPost("transfer")]
        public async Task<ActionResult> TransferStock([FromBody] TransferStockRequest request)
        {
            try
            {
                if (request.Quantity <= 0)
                {
                    return BadRequest(new { message = "Количество для переноса должно быть положительным" });
                }

                var result = await _inventoryRepository.TransferStockAsync(request.FromId, request.ToId, request.Quantity);
                if (!result)
                {
                    return BadRequest(new { message = "Не удалось выполнить перенос запасов" });
                }

                return NoContent();
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Ошибка при переносе запасов");
                return StatusCode(500, new { message = "Внутренняя ошибка сервера" });
            }
        }

        [HttpDelete("{id}")]
        public async Task<ActionResult> Delete(int id)
        {
            try
            {
                if (!await _inventoryRepository.ExistsAsync(id))
                {
                    return NotFound(new { message = "Складская позиция не найдена" });
                }

                var result = await _inventoryRepository.DeleteAsync(id);
                if (!result)
                {
                    return BadRequest(new { message = "Не удалось удалить складскую позицию" });
                }

                return NoContent();
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Ошибка при удалении складской позиции с ID: {Id}", id);
                return StatusCode(500, new { message = "Внутренняя ошибка сервера" });
            }
        }

        [HttpGet("total-value")]
        public async Task<ActionResult<decimal>> GetTotalValue()
        {
            try
            {
                var value = await _inventoryRepository.GetTotalValueAsync();
                return Ok(value);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Ошибка при расчете общей стоимости склада");
                return StatusCode(500, new { message = "Внутренняя ошибка сервера" });
            }
        }

        [HttpGet("product/{productId}/total-quantity")]
        public async Task<ActionResult<int>> GetTotalQuantityByProduct(int productId)
        {
            try
            {
                if (!await _productRepository.ExistsAsync(productId))
                {
                    return NotFound(new { message = "Товар не найден" });
                }

                var quantity = await _inventoryRepository.GetTotalQuantityAsync(productId);
                return Ok(quantity);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Ошибка при получении общего количества товара");
                return StatusCode(500, new { message = "Внутренняя ошибка сервера" });
            }
        }
    }

    public class CreateInventoryRequest
    {
        public int? ProductId { get; set; }
        public int? BatchId { get; set; }
        public int Quantity { get; set; }
        public DateTime? ReceiptDate { get; set; }
        public string? StorageLocation { get; set; }
        public string? StorageTemperature { get; set; }
        public string? HumidityLevel { get; set; }
    }

    public class UpdateInventoryRequest
    {
        public int? ProductId { get; set; }
        public int? BatchId { get; set; }
        public int? Quantity { get; set; }
        public DateTime? ReceiptDate { get; set; }
        public string? StorageLocation { get; set; }
        public string? StorageTemperature { get; set; }
        public string? HumidityLevel { get; set; }
        public bool? IsActive { get; set; }
    }

    public class UpdateQuantityRequest
    {
        public int Quantity { get; set; }
    }

    public class TransferStockRequest
    {
        public int FromId { get; set; }
        public int ToId { get; set; }
        public int Quantity { get; set; }
    }
}