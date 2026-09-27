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
    public class CategoriesController : ControllerBase
    {
        private readonly ICategoryRepository _categoryRepository;
        private readonly AppDbContext _context;
        private readonly ILogger<CategoriesController> _logger;

        public CategoriesController(
            ICategoryRepository categoryRepository,
            Data.AppDbContext context,
            ILogger<CategoriesController> logger)
        {
            _categoryRepository = categoryRepository;
            _context = context;
            _logger = logger;
        }

        [HttpGet]
        public async Task<ActionResult<IEnumerable<Category>>> GetAll()
        {
            try
            {
                var categories = await _categoryRepository.GetAllAsync();
                return Ok(categories);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Ошибка при получении категорий");
                return StatusCode(500, new { message = "Внутренняя ошибка сервера" });
            }
        }

        [HttpGet("{id}")]
        public async Task<ActionResult<Category>> GetById(int id)
        {
            try
            {
                var category = await _categoryRepository.GetByIdAsync(id);
                if (category == null)
                {
                    return NotFound(new { message = "Категория не найдена" });
                }

                return Ok(category);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Ошибка при получении категории с ID: {Id}", id);
                return StatusCode(500, new { message = "Внутренняя ошибка сервера" });
            }
        }

        [HttpPost]
        public async Task<ActionResult<Category>> Create([FromBody] CreateCategoryRequest request)
        {
            try
            {
                if (string.IsNullOrEmpty(request.Name))
                {
                    return BadRequest(new { message = "Название категории обязательно" });
                }

                if (await _categoryRepository.NameExistsAsync(request.Name))
                {
                    return Conflict(new { message = "Категория с таким названием уже существует" });
                }

                var category = new Category
                {
                    Name = request.Name,
                    Description = request.Description
                };

                var createdCategory = await _categoryRepository.CreateAsync(category);
                return CreatedAtAction(nameof(GetById), new { id = createdCategory.ID }, createdCategory);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Ошибка при создании категории");
                return StatusCode(500, new { message = "Внутренняя ошибка сервера" });
            }
        }

        [HttpPut("{id}")]
        public async Task<ActionResult<Category>> Update(int id, [FromBody] UpdateCategoryRequest request)
        {
            try
            {
                var existingCategory = await _categoryRepository.GetByIdAsync(id);
                if (existingCategory == null)
                {
                    return NotFound(new { message = "Категория не найдена" });
                }

                if (string.IsNullOrEmpty(request.Name))
                {
                    return BadRequest(new { message = "Название категории обязательно" });
                }

                if (await _categoryRepository.NameExistsAsync(request.Name, id))
                {
                    return Conflict(new { message = "Категория с таким названием уже существует" });
                }

                existingCategory.Name = request.Name;
                existingCategory.Description = request.Description;

                var updatedCategory = await _categoryRepository.UpdateAsync(existingCategory);
                return Ok(new { category = updatedCategory, ID = updatedCategory.ID });
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Ошибка при обновлении категории с ID: {ID}", id);
                return StatusCode(500, new { message = "Внутренняя ошибка сервера" });
            }
        }

        [HttpDelete("{id}")]
        public async Task<ActionResult> Delete(int id)
        {
            try
            {
                if (!await _categoryRepository.ExistsAsync(id))
                {
                    return NotFound(new { message = "Категория не найдена" });
                }

                if (await _context.Product.AnyAsync(p => p.CategoryID == id))
                {
                    return Conflict(new { message = "Нельзя удалить категорию: есть связанные товары" });
                }
                var result = await _categoryRepository.DeleteAsync(id);
                if (!result)
                {
                    return BadRequest(new { message = "Не удалось удалить категорию" });
                }

                return NoContent();
            }
            catch (Microsoft.EntityFrameworkCore.DbUpdateException dbEx)
            {
                _logger.LogWarning(dbEx, "Нарушение внешнего ключа при удалении");
                return Conflict(new { message = "Нельзя удалить категорию: есть связанные товары" });
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Ошибка при удалении категории с ID: {Id}", id);
                return StatusCode(500, new { message = "Внутренняя ошибка сервера" });
            }
        }
    }

    public class CreateCategoryRequest
    {
        public string Name { get; set; } = string.Empty;
        public string? Description { get; set; }
    }

    public class UpdateCategoryRequest
    {
        public string Name { get; set; } = string.Empty;
        public string? Description { get; set; }
    }
}