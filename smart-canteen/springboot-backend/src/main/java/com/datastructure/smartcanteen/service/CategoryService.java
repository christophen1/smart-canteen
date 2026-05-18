package com.datastructure.smartcanteen.service;

import com.datastructure.smartcanteen.entity.Category;

import java.util.List;

public interface CategoryService {

    List<Category> list();

    Category getById(Long id);

    void save(Category category);

    void update(Category category);

    void delete(Long id);
}
