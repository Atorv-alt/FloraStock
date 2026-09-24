using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Core.Interfaces;
using Shared.Entities;

namespace API.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    [Authorize]
    public class ProductsController : ControllerBase
    {
        private readonly IProductRepository _productRepository;
        private readonly ICategoryRepository _categoryRepository;
        private readonly ILogger<ProductsController> _logger;

        public ProductsController(
            IProductRepository productRepository,
            ICategoryRepository categoryRepository,
            ILogger<ProductsController> logger)
        {
            _productRepository = productRepository;
            _categoryRepository = categoryRepository;
            _logger = logger;
        }

        [HttpGet]
        public async Task<ActionResult<IEnumerable<Product>>> GetAll()
        {
            try
            {
                var products = await _productRepository.GetAllAsync();
                return Ok(products);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Ошибка при получении товаров");
                return StatusCode(500, new { message = "Внутренняя ошибка сервера" });
            }
        }

        [HttpGet("active")]
        public async Task<ActionResult<IEnumerable<Product>>> GetActive()
        {
            try
            {
                var products = await _productRepository.GetActiveAsync();
                return Ok(products);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Ошибка при получении активных товаров");
                return StatusCode(500, new { message = "Внутренняя ошибка сервера" });
            }
        }

        [HttpGet("category/{categoryId}")]
        public async Task<ActionResult<IEnumerable<Product>>> GetByCategory(int categoryId)
        {
            try
            {
                if (!await _categoryRepository.ExistsAsync(categoryId))
                {
                    return NotFound(new { message = "Категория не найдена" });
                }

                var products = await _productRepository.GetByCategoryAsync(categoryId);
                return Ok(products);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Ошибка при получении товаров по категории");
                return StatusCode(500, new { message = "Внутренняя ошибка сервера" });
            }
        }

        [HttpGet("low-stock")]
        public async Task<ActionResult<IEnumerable<Product>>> GetLowStock([FromQuery] int threshold = 10)
        {
            try
            {
                var products = await _productRepository.GetLowStockAsync(threshold);
                return Ok(products);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Ошибка при получении товаров с низким остатком");
                return StatusCode(500, new { message = "Внутренняя ошибка сервера" });
            }
        }

        [HttpGet("{id}")]
        public async Task<ActionResult<Product>> GetById(int id)
        {
            try
            {
                var product = await _productRepository.GetByIdAsync(id);
                if (product == null)
                {
                    return NotFound(new { message = "Товар не найден" });
                }

                return Ok(product);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Ошибка при получении товара с ID: {Id}", id);
                return StatusCode(500, new { message = "Внутренняя ошибка сервера" });
            }
        }

        [HttpPost]
        public async Task<ActionResult<Product>> Create([FromBody] CreateProductRequest request)
        {
            try
            {
                if (string.IsNullOrEmpty(request.Name))
                {
                    return BadRequest(new { message = "Название товара обязательно" });
                }

                if (request.CategoryId.HasValue && !await _categoryRepository.ExistsAsync(request.CategoryId.Value))
                {
                    return BadRequest(new { message = "Указанная категория не существует" });
                }

                if (await _productRepository.NameExistsAsync(request.Name))
                {
                    return Conflict(new { message = "Товар с таким названием уже существует" });
                }

                var product = new Product
                {
                    Name = request.Name,
                    Description = request.Description,
                    CategoryId = request.CategoryId,
                    Unit = request.Unit ?? "шт",
                    PurchasePrice = request.PurchasePrice,
                    RetailPrice = request.RetailPrice,
                    ShelfLifeDays = request.ShelfLifeDays,
                    Color = request.Color,
                    StemLengthCm = request.StemLengthCm
                };

                var createdProduct = await _productRepository.CreateAsync(product);
                return CreatedAtAction(nameof(GetById), new { id = createdProduct.ID }, createdProduct);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Ошибка при создании товара");
                return StatusCode(500, new { message = "Внутренняя ошибка сервера" });
            }
        }

        [HttpPut("{id}")]
        public async Task<ActionResult<Product>> Update(int id, [FromBody] UpdateProductRequest request)
        {
            try
            {
                var existingProduct = await _productRepository.GetByIdAsync(id);
                if (existingProduct == null)
                {
                    return NotFound(new { message = "Товар не найден" });
                }

                if (string.IsNullOrEmpty(request.Name))
                {
                    return BadRequest(new { message = "Название товара обязательно" });
                }

                if (request.CategoryId.HasValue && !await _categoryRepository.ExistsAsync(request.CategoryId.Value))
                {
                    return BadRequest(new { message = "Указанная категория не существует" });
                }

                if (await _productRepository.NameExistsAsync(request.Name, id))
                {
                    return Conflict(new { message = "Товар с таким названием уже существует" });
                }

                existingProduct.Name = request.Name;
                existingProduct.Description = request.Description;
                existingProduct.CategoryId = request.CategoryId;
                existingProduct.Unit = request.Unit ?? existingProduct.Unit;
                existingProduct.PurchasePrice = request.PurchasePrice;
                existingProduct.RetailPrice = request.RetailPrice;
                existingProduct.ShelfLifeDays = request.ShelfLifeDays;
                existingProduct.Color = request.Color;
                existingProduct.StemLengthCm = request.StemLengthCm;

                var updatedProduct = await _productRepository.UpdateAsync(existingProduct);
                return Ok(updatedProduct);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Ошибка при обновлении товара с ID: {Id}", id);
                return StatusCode(500, new { message = "Внутренняя ошибка сервера" });
            }
        }

        [HttpDelete("{id}")]
        public async Task<ActionResult> Delete(int id)
        {
            try
            {
                if (!await _productRepository.ExistsAsync(id))
                {
                    return NotFound(new { message = "Товар не найден" });
                }

                var result = await _productRepository.DeleteAsync(id);
                if (!result)
                {
                    return BadRequest(new { message = "Не удалось удалить товар" });
                }

                return NoContent();
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Ошибка при удалении товара с ID: {Id}", id);
                return StatusCode(500, new { message = "Внутренняя ошибка сервера" });
            }
        }

        [HttpGet("inventory-value")]
        public async Task<ActionResult<decimal>> GetInventoryValue()
        {
            try
            {
                var value = await _productRepository.GetTotalInventoryValueAsync();
                return Ok(value);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Ошибка при расчете стоимости склада");
                return StatusCode(500, new { message = "Внутренняя ошибка сервера" });
            }
        }
    }

    public class CreateProductRequest
    {
        public string Name { get; set; } = string.Empty;
        public string? Description { get; set; }
        public int? CategoryId { get; set; }
        public string? Unit { get; set; }
        public decimal PurchasePrice { get; set; }
        public decimal RetailPrice { get; set; }
        public int ShelfLifeDays { get; set; } = 7;
        public string? Color { get; set; }
        public int? StemLengthCm { get; set; }
    }

    public class UpdateProductRequest
    {
        public string Name { get; set; } = string.Empty;
        public string? Description { get; set; }
        public int? CategoryId { get; set; }
        public string? Unit { get; set; }
        public decimal PurchasePrice { get; set; }
        public decimal RetailPrice { get; set; }
        public int ShelfLifeDays { get; set; } = 7;
        public string? Color { get; set; }
        public int? StemLengthCm { get; set; }
        public bool IsActive { get; set; } = true;
    }
}