# Frontend Testing Checklist

## Test Environment Setup
1. Backend server running on http://localhost:8888
2. Frontend served on http://localhost:5500 (or similar)
3. PostgreSQL database running with migrations applied
4. Two browser windows/tabs for WebSocket testing

## 1. Registration & Login ✓
- [ ] Open signup.html
- [ ] Register a new user (testuser1)
- [ ] Verify success message and redirect to login
- [ ] Login with new credentials
- [ ] Verify redirect to dashboard

## 2. Dashboard & Profile ✓
- [ ] Dashboard loads with welcome message
- [ ] User name displayed correctly
- [ ] Navigate to Profile page
- [ ] Profile information displayed correctly
- [ ] Navigate back to Dashboard

## 3. Communities Listing ✓
- [ ] Navigate to Communities page
- [ ] Verify 3 default communities are displayed:
  - Mindful Moments
  - Healing Together
  - Calm Circle
- [ ] Each community shows:
  - Name
  - Description
  - Member count
  - Join button (if not member)

## 4. Join Community ✓
- [ ] Click "Join" on first community
- [ ] Button changes to loading state
- [ ] Success toast appears
- [ ] Community card updates to show "Chat" and "Leave" buttons
- [ ] Member count increments

## 5. Real-time Chat - Single User ✓
- [ ] Click "Chat" button on joined community
- [ ] Chat panel opens with community name
- [ ] Connection status shows "✅ Connected"
- [ ] Type a message and press Enter
- [ ] Message appears in chat with username and timestamp
- [ ] Message is right-aligned (own message style)

## 6. Real-time Chat - Multiple Users ✓
**In first browser (testuser1):**
- [ ] Stay in open chat

**In second browser/tab:**
- [ ] Register/login as testuser2
- [ ] Navigate to Communities
- [ ] Join the same community as testuser1
- [ ] Open chat for that community
- [ ] Send a message
- [ ] Verify message appears in both browsers
- [ ] Verify testuser1 sees testuser2's message (left-aligned)
- [ ] Verify testuser2 sees their own message (right-aligned)

**Back in first browser:**
- [ ] Send a reply from testuser1
- [ ] Verify message appears in both browsers in real-time

## 7. Feed - Create Post ✓
- [ ] Navigate to Dashboard
- [ ] Enter text in "Share Your Thoughts" textarea
- [ ] Select "General Feed" (default)
- [ ] Click "Post" button
- [ ] Button shows loading state
- [ ] Success toast appears
- [ ] New post appears at top of feed with:
  - Username
  - Timestamp
  - Content (safely rendered)
  - Delete button (if own post)

## 8. Feed - Create Community Post ✓
- [ ] Verify dropdown shows joined communities
- [ ] Select a joined community
- [ ] Enter post content
- [ ] Click "Post"
- [ ] Verify post appears with community tag

## 9. Feed - Delete Post ✓
- [ ] Find your own post in feed
- [ ] Verify "Delete" button is visible
- [ ] Click "Delete"
- [ ] Confirm deletion dialog
- [ ] Post disappears with fade animation
- [ ] Success toast appears

**Test permissions:**
- [ ] Login as testuser2
- [ ] Try to delete testuser1's post
- [ ] Verify no delete button appears

## 10. Loading States ✓
- [ ] Refresh Communities page
- [ ] Verify spinner shows "Loading communities..."
- [ ] Refresh Dashboard
- [ ] Verify posts show "Loading posts..."
- [ ] Close chat and reopen
- [ ] Verify messages show "Loading messages..."

## 11. Empty States ✓
- [ ] Join a new community with no messages
- [ ] Open chat
- [ ] Verify empty state: "No messages yet. Start the conversation!" 💬
- [ ] Create new account (no posts)
- [ ] Verify empty feed: "No posts yet. Be the first to share!" 📝

## 12. Error States ✓
- [ ] Disconnect internet
- [ ] Try to load communities
- [ ] Verify error message appears
- [ ] Try to send chat message when disconnected
- [ ] Verify toast: "Not connected to chat"
- [ ] Reconnect internet
- [ ] Verify auto-reconnect with exponential backoff

## 13. XSS Prevention ✓
- [ ] Try to create post with HTML: `<script>alert('XSS')</script>`
- [ ] Verify content is displayed as text (not executed)
- [ ] Try to send chat message with HTML tags
- [ ] Verify message renders safely as text
- [ ] Check profile fields render safely

## 14. Navigation & Logout ✓
- [ ] Click all navigation links
- [ ] Verify navigation works correctly
- [ ] Click Logout
- [ ] Confirm logout dialog
- [ ] Verify redirect to landing page
- [ ] Try to access dashboard.html directly
- [ ] Verify redirect to login page

## 15. Mobile Responsiveness
- [ ] Resize browser to mobile width (< 768px)
- [ ] Verify communities list stacks vertically
- [ ] Verify chat panel fits mobile screen
- [ ] Verify buttons are full-width on mobile
- [ ] Verify navigation adapts
- [ ] Test on actual mobile device if available

## 16. WebSocket Reconnection
- [ ] Open chat
- [ ] Simulate disconnect (close server briefly)
- [ ] Verify status shows "⚠️ Disconnected"
- [ ] Restart server
- [ ] Verify auto-reconnect
- [ ] Verify status shows "✅ Connected"
- [ ] Send message to verify functionality restored

## Backend Compatibility Checks
- [x] WebSocket expects `user_id` and `message` fields
- [x] GET /api/communities returns correct structure
- [x] POST /api/posts accepts `content` and `community_id`
- [x] GET /api/posts returns posts with `can_delete` flag
- [x] DELETE /api/posts/{id} enforces permissions

## Known Limitations
1. Translation is disabled (TRANSLATION_ENABLED=false)
2. Language preference defaults to English
3. No pagination on posts yet (limit=50)
4. WebSocket doesn't persist auth across page reloads (reconnects each time)

## Success Criteria
All checkboxes must be checked for complete verification.

---

## Quick Test Flow (5 minutes)
1. Register → Login → Dashboard ✓
2. Navigate to Communities → Join one → Open chat ✓
3. Send message → See it appear ✓
4. Open second browser → Login → Join same community → Open chat ✓
5. Send message from both browsers → Verify real-time sync ✓
6. Create post on Dashboard → Verify it appears → Delete it ✓
7. Logout → Verify redirect ✓

**If all 7 steps pass, the implementation is working correctly.**
