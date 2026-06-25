Jekyll::Hooks.register :site, :post_read do |site|
  if site.config['public_only']
    site.pages.reject! do |p|
      %w[.md .markdown].include?(File.extname(p.path)) && p.data['domain'] != 'public'
    end
  end
end
