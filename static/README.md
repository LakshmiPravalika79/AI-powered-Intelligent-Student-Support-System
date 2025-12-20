# Static Files - Frontend 🎨

This folder contains the **single-page application** frontend.

## File

### `index.html` - Complete Web UI

A fully functional frontend built with:
- **HTML5** - Semantic markup
- **Tailwind CSS** (CDN) - Utility-first styling
- **Vanilla JavaScript** - No framework dependencies
- **Font Awesome** (CDN) - Icons

## Features

### Login Screen
- Email/password authentication
- Role-based redirection
- Error handling

### Student Portal
- **Chat Interface**: Talk to AI assistant
- **Quick Questions**: Pre-built query buttons
- **My Tickets**: View support tickets and staff replies
- **Profile View**: Academic info, financial aid, housing

### Staff Portal
- **Ticket Queue**: View all open tickets
- **Ticket Details**: Full conversation thread
- **Reply System**: Respond to students
- **Status Management**: Update ticket status

### Admin Dashboard
- **Analytics**: Query volume, resolution rates
- **Legacy Systems**: Health monitoring
- **RBAC Matrix**: Permission overview
- **Architecture Diagram**: System visualization

## Why No Framework?

1. **Zero Build Step**: Just open the HTML file
2. **No Node.js Required**: No npm, webpack, etc.
3. **Fast Loading**: CDN-delivered CSS/JS
4. **Easy to Demo**: Works anywhere
5. **Hackathon Speed**: Quick to develop

## Styling

Uses Tailwind CSS utility classes:
```html
<!-- Example: Styled button -->
<button class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg">
    Click Me
</button>
```

## JavaScript Architecture

All functionality in vanilla JS:
```javascript
// API calls
const response = await fetch(`${API_URL}/api/chat`, {
    method: 'POST',
    headers: { 
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({ student_id, message })
});

// Dynamic UI updates
function addMessage(type, text) {
    const chatMessages = document.getElementById('chatMessages');
    // ... create and append message element
}
```

## Responsive Design

Works on desktop and mobile using Tailwind responsive classes:
```html
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
```
