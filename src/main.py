import asyncio
import sys
from pathlib import Path
import click
from dotenv import load_dotenv
from .agent.query_classifier import QueryClassifier
from .generators.registry import GeneratorRegistry
from .processors.pixel_art import convert_to_pixel_art, enhance_pixel_art_prompt
from .utils.file_manager import OutputManager
from .utils.logger import setup_logger


# Load environment variables
load_dotenv()

# Setup logger
logger = setup_logger('16pixels')


@click.command()
@click.option(
    '--query', '-q',
    required=True,
    help='Image generation query'
)
@click.option(
    '--variations', '-v',
    type=click.IntRange(1, 4),
    default=1,
    help='Number of variations to generate per provider (1-4)'
)
@click.option(
    '--output-dir', '-o',
    type=click.Path(),
    default='./output',
    help='Output directory for generated images'
)
@click.option(
    '--no-pixel-art',
    is_flag=True,
    help='Skip pixel art conversion (save original resolution)'
)
@click.option(
    '--debug',
    is_flag=True,
    help='Enable debug logging'
)
def main(query: str, variations: int, output_dir: str, no_pixel_art: bool, debug: bool):
    """
    16-Pixels: AI-powered 16x16 pixel art generator.
    
    This tool uses Google Gemini to determine if your query is for image generation,
    then generates pixel art from multiple AI providers.
    """
    if debug:
        import logging
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Run the async main function
    asyncio.run(async_main(query, variations, output_dir, no_pixel_art))


async def async_main(query: str, variations: int, output_dir: str, no_pixel_art: bool):
    """Async main function to handle the image generation pipeline."""
    
    try:
        # Step 1: Classify the query
        logger.info("Classifying query...")
        classifier = QueryClassifier()
        classification = await classifier.classify(query)
        
        logger.info(f"Classification: is_image_request={classification.is_image_request}, "
                   f"confidence={classification.confidence:.2f}")
        
        if not classification.is_image_request:
            logger.error(f"Request rejected: {classification.rejection_reason}")
            click.echo(click.style(f"❌ Request rejected: {classification.rejection_reason}", fg='red'))
            sys.exit(1)
        
        # Step 2: Enhance prompt for pixel art if needed
        generation_prompt = classification.image_description or query
        if not no_pixel_art:
            generation_prompt = enhance_pixel_art_prompt(generation_prompt)
        
        logger.info(f"Generation prompt: {generation_prompt}")
        
        # Step 3: Initialize output manager and create session
        output_manager = OutputManager(output_dir)
        session_path = output_manager.create_session_folder()
        click.echo(click.style(f"📁 Creating images in: {session_path}", fg='blue'))
        
        # Step 4: Initialize generator registry
        registry = GeneratorRegistry()
        available_generators = registry.get_available_generators()
        
        if not available_generators:
            logger.error("No image generators available")
            click.echo(click.style("❌ No image generators available. Please configure API keys.", fg='red'))
            sys.exit(1)
        
        click.echo(click.style(f"🎨 Generating images from {len(available_generators)} providers: "
                             f"{', '.join(available_generators)}", fg='green'))
        
        # Step 5: Generate images from all providers
        all_results = await registry.generate_all(generation_prompt, variations)
        
        # Step 6: Process and save images
        total_saved = 0
        for provider, results in all_results.items():
            provider_saved = 0
            
            for i, image in enumerate(results['images'], 1):
                try:
                    # Convert to pixel art if requested
                    if not no_pixel_art:
                        processed_image = convert_to_pixel_art(image)
                    else:
                        processed_image = image
                    
                    # Save the image
                    output_manager.save_image(processed_image, provider, i, session_path)
                    provider_saved += 1
                    total_saved += 1
                    
                except Exception as e:
                    logger.error(f"Failed to save image from {provider}: {e}")
            
            if provider_saved > 0:
                click.echo(f"  ✓ {provider}: {provider_saved} images")
            else:
                click.echo(click.style(f"  ✗ {provider}: failed", fg='red'))
        
        # Step 7: Save metadata
        classification_dict = {
            'is_image_request': classification.is_image_request,
            'confidence': classification.confidence,
            'image_description': classification.image_description,
            'rejection_reason': classification.rejection_reason
        }
        output_manager.save_metadata(query, classification_dict, all_results, session_path)
        
        # Step 8: Show summary
        click.echo(click.style(f"\n✨ Generated {total_saved} images total", fg='green', bold=True))
        click.echo(f"\n{output_manager.create_session_summary(session_path)}")
        
    except KeyboardInterrupt:
        logger.info("Generation cancelled by user")
        click.echo(click.style("\n⚠️  Generation cancelled", fg='yellow'))
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        click.echo(click.style(f"\n❌ Error: {e}", fg='red'))
        sys.exit(1)


if __name__ == '__main__':
    main()