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
    }
}
