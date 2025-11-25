import { readFileSync } from 'fs';

console.log('🔍 Testing Settings Page Back Button Navigation');
console.log('='.repeat(50));

try {
  // Read the Settings page
  const settingsPage = readFileSync('./src/pages/Settings.tsx', 'utf8');
  
  // Check if useNavigate is imported
  if (settingsPage.includes('useNavigate') && settingsPage.includes('react-router-dom')) {
    console.log('✅ useNavigate hook imported correctly');
  } else {
    console.log('❌ useNavigate hook not found or incorrectly imported');
  }
  
  // Check if navigate function is defined
  if (settingsPage.includes('const navigate = useNavigate()')) {
    console.log('✅ navigate function defined correctly');
  } else {
    console.log('❌ navigate function not defined');
  }
  
  // Check if back button has onClick handler
  if (settingsPage.includes('onClick={() => navigate(\'/dashboard\')}')) {
    console.log('✅ Back button onClick handler configured correctly');
  } else {
    console.log('❌ Back button onClick handler missing or incorrect');
  }
  
  // Check if ArrowLeft icon is imported
  if (settingsPage.includes('ArrowLeft')) {
    console.log('✅ ArrowLeft icon imported correctly');
  } else {
    console.log('❌ ArrowLeft icon not imported');
  }
  
  console.log('\n🔧 SUGGESTED FIX:');
  console.log('If the button is not working, try changing navigate(\'/dashboard\') to navigate(-1) to go back one page in history.');
  
} catch (error) {
  console.log('❌ Error testing Settings page:', error.message);
}