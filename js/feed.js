// Feed Module
// Handles post creation, listing, and deletion

class Feed {
    constructor() {
        this.posts = [];
        this.currentCommunityFilter = null;
    }

    // Load and render posts
    async loadPosts(communityId = null) {
        const container = document.getElementById('feed-posts');
        if (!container) return;

        UI.showLoading(container, 'Loading posts...');

        const result = await API.getPosts(communityId);

        if (!result.success) {
            UI.showError(container, result.error || 'Failed to load posts');
            return;
        }

        this.posts = result.data.posts || [];
        this.currentCommunityFilter = communityId;

        if (this.posts.length === 0) {
            UI.showEmpty(container, 'No posts yet. Be the first to share!', '📝');
            return;
        }

        this.renderPosts(container);
    }

    // Render posts
    renderPosts(container) {
        container.innerHTML = '';

        this.posts.forEach(post => {
            const postCard = this.createPostCard(post);
            container.appendChild(postCard);
        });
    }

    // Create post card element
    createPostCard(post) {
        const card = document.createElement('div');
        card.className = 'card post-card';
        card.style.cssText = 'margin-bottom: 15px;';
        card.dataset.postId = post.id;

        // Header
        const header = document.createElement('div');
        header.style.cssText = 'display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;';

        const authorInfo = document.createElement('div');
        const authorName = document.createElement('strong');
        authorName.textContent = post.username;
        authorName.style.cssText = 'font-size: 16px; color: #333;';

        const postTime = document.createElement('span');
        postTime.style.cssText = 'font-size: 12px; color: #999; margin-left: 10px;';
        postTime.textContent = UI.formatDate(post.created_at);

        authorInfo.appendChild(authorName);
        authorInfo.appendChild(postTime);

        header.appendChild(authorInfo);

        // Delete button if user can delete
        if (post.can_delete) {
            const deleteBtn = document.createElement('button');
            deleteBtn.className = 'btn btn-red';
            deleteBtn.textContent = 'Delete';
            deleteBtn.style.cssText = 'padding: 6px 12px; font-size: 13px;';
            deleteBtn.onclick = () => this.deletePost(post.id, card);
            header.appendChild(deleteBtn);
        }

        // Community tag if applicable
        if (post.community_id) {
            const communityTag = document.createElement('span');
            communityTag.style.cssText = `
                display: inline-block;
                background: #e3f2fd;
                color: #0066cc;
                padding: 4px 10px;
                border-radius: 12px;
                font-size: 12px;
                font-weight: 500;
                margin-bottom: 10px;
            `;
            communityTag.textContent = '🏘️ Community Post';
            card.appendChild(communityTag);
        }

        card.appendChild(header);

        // Content
        const content = document.createElement('div');
        content.className = 'post-content';
        content.style.cssText = 'color: #555; line-height: 1.6; white-space: pre-wrap; word-wrap: break-word;';
        content.textContent = post.content; // Safe rendering via textContent

        card.appendChild(content);

        return card;
    }

    // Create new post
    async createPost() {
        const contentInput = document.getElementById('post-content');
        const communitySelect = document.getElementById('post-community');
        const submitBtn = document.getElementById('post-submit');

        const content = contentInput.value.trim();
        if (!content) {
            UI.showToast('Please enter some content', 'warning');
            return;
        }

        const communityId = communitySelect && communitySelect.value !== ''
            ? communitySelect.value
            : null;

        const originalText = UI.disableButton(submitBtn, 'Posting...');

        const result = await API.createPost(content, communityId);

        if (result.success) {
            UI.showToast('Post created successfully!', 'success');
            contentInput.value = '';
            if (communitySelect) communitySelect.value = '';

            // Reload posts
            await this.loadPosts(this.currentCommunityFilter);
        } else {
            UI.showToast(result.error || 'Failed to create post', 'error');
        }

        UI.enableButton(submitBtn, originalText);
    }

    // Delete post
    async deletePost(postId, cardElement) {
        if (!UI.confirm('Are you sure you want to delete this post?')) {
            return;
        }

        const deleteBtn = cardElement.querySelector('.btn-red');
        if (deleteBtn) {
            const originalText = UI.disableButton(deleteBtn, 'Deleting...');

            const result = await API.deletePost(postId);

            if (result.success) {
                UI.showToast('Post deleted successfully', 'success');
                // Remove card with animation
                cardElement.style.transition = 'opacity 0.3s ease';
                cardElement.style.opacity = '0';
                setTimeout(() => {
                    cardElement.remove();
                    // Check if feed is now empty
                    const container = document.getElementById('feed-posts');
                    if (container && container.children.length === 0) {
                        UI.showEmpty(container, 'No posts yet. Be the first to share!', '📝');
                    }
                }, 300);
            } else {
                UI.showToast(result.error || 'Failed to delete post', 'error');
                if (deleteBtn) {
                    UI.enableButton(deleteBtn, originalText);
                }
            }
        }
    }

    // Load communities for dropdown
    async loadCommunitiesForDropdown() {
        const select = document.getElementById('post-community');
        if (!select) return;

        const result = await API.getCommunities();

        if (result.success && result.data.communities) {
            const joinedCommunities = result.data.communities.filter(c => c.is_member);

            select.innerHTML = '<option value="">General Feed</option>';

            joinedCommunities.forEach(community => {
                const option = document.createElement('option');
                option.value = community.id;
                option.textContent = community.name;
                select.appendChild(option);
            });
        }
    }
}

// Initialize on page load
let feedManager;

document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('feed-posts')) {
        feedManager = new Feed();
        feedManager.loadPosts();

        // Load communities for dropdown if present
        if (document.getElementById('post-community')) {
            feedManager.loadCommunitiesForDropdown();
        }

        // Set up post submission
        const submitBtn = document.getElementById('post-submit');
        if (submitBtn) {
            submitBtn.onclick = () => feedManager.createPost();
        }

        // Set up community filter if present
        const communityFilter = document.getElementById('feed-community-filter');
        if (communityFilter) {
            communityFilter.onchange = (e) => {
                const communityId = e.target.value || null;
                feedManager.loadPosts(communityId);
            };
        }
    }
});

// Export to global scope
window.Feed = Feed;
window.feedManager = feedManager;
