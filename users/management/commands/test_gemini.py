from django.core.management.base import BaseCommand
from allflex.gym_recommender import GymFinder

class Command(BaseCommand):
    help = 'Test Gemini API gym finder'

    def handle(self, *args, **options):
        self.stdout.write("=" * 60)
        self.stdout.write("Testing Gemini Gym Finder from Django")
        self.stdout.write("=" * 60)
        
        finder = GymFinder()
        
        if not finder.client:
            self.stdout.write(self.style.ERROR("No Gemini client initialized - API key issue!"))
            self.stdout.write(f"API Key starts with: {finder.api_key[:20] if finder.api_key else 'None'}...")
        else:
            self.stdout.write(self.style.SUCCESS(f"Gemini client initialized with model: {finder.model_name}"))
        
        # Test search
        self.stdout.write("\nTesting search for pincode 400001...")
        result = finder.find_gyms("400001")
        
        if "error" in result:
            self.stdout.write(self.style.ERROR(f"Error: {result['error']}"))
        else:
            self.stdout.write(self.style.SUCCESS(f"Found {len(result)} gyms:"))
            for i, (name, info) in enumerate(list(result.items())[:5], 1):
                if isinstance(info, dict):
                    self.stdout.write(f"  {i}. {name} - {info.get('distance')}, Rating: {info.get('rating')}")
